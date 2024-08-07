import os
import threading
import cv2
from deepface import DeepFace
from queue import Queue
import mediapipe as mp
import numpy as np
import time
import serial

# Set the TensorFlow environment variable to turn off oneDNN custom operations
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

def initialize_serial(port, baudrate):
    while True:
        try:
            arduino = serial.Serial(port, baudrate, timeout=1)
            time.sleep(2)
            print("Serial connection established on", port)
            return arduino
        except serial.SerialException as e:
            print(f"Failed to connect on {port}: {e}")
            time.sleep(5)
            continue

arduino = initialize_serial('COM9', 9600)    # Change COM9 to the actual communication port once the arduino is connected. 

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

counter = 0
face_match = False
lock = threading.Lock()
task_queue = Queue()

# Load multiple reference images
reference_img_paths = [
    r"C:\Users\nikhi\OneDrive\Documents\Github\Pose-Estimation-Autonomous-Turret\FacialRecognition\Nikhil.jpg",   # Nikhil
    r"C:\Users\nikhi\OneDrive\Documents\Github\Pose-Estimation-Autonomous-Turret\FacialRecognition\Nikhil2.jpg",  # Nikhil 2
    r"C:\Users\nikhi\OneDrive\Documents\Github\Pose-Estimation-Autonomous-Turret\FacialRecognition\Nikhil3.jpg",  # Nikhil 3
    r"C:\Users\nikhi\OneDrive\Documents\Github\Pose-Estimation-Autonomous-Turret\FacialRecognition\Nikhil4.jpg",  # Nikhil 4
    r"C:\Users\nikhi\OneDrive\Documents\Github\Pose-Estimation-Autonomous-Turret\FacialRecognition\Nikhil5.jpg",  # Nikhil 5
]
reference_imgs = [cv2.imread(path) for path in reference_img_paths]

# Check if all images were loaded correctly
for path, img in zip(reference_img_paths, reference_imgs):
    if img is None:
        print(f"Error: Could not load the image at path {path}")
        exit()

face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def check_face():
    global face_match
    while True:
        frame, face_coords = task_queue.get()
        try:
            (x, y, w, h) = face_coords
            face_img = frame[y:y+h, x:x+w]
            match_found = False
            for ref_img in reference_imgs:
                try:
                    result = DeepFace.verify(face_img, ref_img.copy(), model_name="VGG-Face", detector_backend="opencv")
                    if result['verified']:
                        match_found = True
                        break
                except Exception as e:
                    print(f"Error verifying with reference image: {e}")
            with lock:
                face_match = match_found
            print(f"Verification result: {result}")
        except Exception as e:
            print(f"Error in face verification: {e}")
            with lock:
                face_match = False
        task_queue.task_done()

# Start a single worker thread
threading.Thread(target=check_face, daemon=True).start()

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

previous_center = None
previous_time = None
pTime = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)

    for (x, y, w, h) in faces:
        if counter % 30 == 0:
            task_queue.put((frame.copy(), (x, y, w, h)))
        counter += 1

        with lock:
            color = (0, 255, 0) if face_match else (0, 0, 255)
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)

        cv2.putText(frame, "MATCH!" if face_match else "NO MATCH!", (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 2, color, 3)

    # Convert the image to RGB for MediaPipe
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = pose.process(img_rgb)

    if result.pose_landmarks:
        mp_drawing.draw_landmarks(frame, result.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        # Extract landmarks
        lmList = [(i, lm.x * frame.shape[1], lm.y * frame.shape[0]) for i, lm in enumerate(result.pose_landmarks.landmark)]

        if len(lmList) > 0:
            # Calculate the midpoint between shoulders (landmarks 11 and 12)
            center = (
                (lmList[11][1] + lmList[12][1]) // 2,
                (lmList[11][2] + lmList[12][2]) // 2
            )

            previous_center = center
            previous_time = time.time()

            # Send the face match status and center coordinates to the Arduino
            try:
                arduino.write(f"{face_match},{center[0]},{center[1]}\n".encode())
            except serial.SerialException as e:
                print(f"Failed to write to serial port: {e}")

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    
    # Add FPS to the image
    cv2.putText(frame, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 255, 0), 2)
    
    cv2.imshow('video', frame)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
arduino.close()
