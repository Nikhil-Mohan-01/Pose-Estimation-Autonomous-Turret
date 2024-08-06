import os
import threading
import cv2
from deepface import DeepFace
from queue import Queue

# Set the TensorFlow environment variable to turn off oneDNN custom operations
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

counter = 0
reference_img_path = r"C:\Users\nikhi\OneDrive\Documents\Github\Pose-Estimation-Autonomous-Turret\FacialRecognition\Nikhil.jpg"
reference_img = cv2.imread(reference_img_path)

# Check if the image was loaded correctly
if reference_img is None:
    print(f"Error: Could not load the image at path {reference_img_path}")
    exit()

face_match = False
lock = threading.Lock()
task_queue = Queue()
face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def check_face():
    global face_match
    while True:
        frame, face_coords = task_queue.get()
        try:
            (x, y, w, h) = face_coords
            face_img = frame[y:y+h, x:x+w]
            result = DeepFace.verify(face_img, reference_img.copy(), model_name="VGG-Face", detector_backend="opencv")
            with lock:
                face_match = result['verified']
            print(f"Verification result: {result}")
        except Exception as e:
            print(f"Error in face verification: {e}")
            with lock:
                face_match = False
        task_queue.task_done()

# Start a single worker thread
threading.Thread(target=check_face, daemon=True).start()

while True:
    ret, frame = cap.read()

    if ret:
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

        cv2.imshow('video', frame)

    key = cv2.waitKey(1)
    if key == ord('q'):
        break

cv2.destroyAllWindows()
cap.release()
