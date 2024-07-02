import cv2
import mediapipe as mp
import time
import numpy as np
import serial

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


arduino = initialize_serial('COM9', 9600)


mp_pose = mp.solutions.pose
pose = mp_pose.Pose()         
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
previous_center = None
previous_time = None

def calculate_speed_and_direction(current_center, previous_center, current_time, previous_time):
    if previous_center is None or previous_time is None:
        return 0, "Still"

    dx = current_center[0] - previous_center[0]
    dy = current_center[1] - previous_center[1]
    dt = current_time - previous_time

    speed_pxs = np.sqrt(dx**2 + dy**2) / dt
    speed_mps = speed_pxs * 0.1

    if dx > 0:
        direction = "Right"
    elif dx < 0:
        direction = "Left"
    else:
        direction = "Still"

    return speed_mps, direction

while True:
    success, img = cap.read()
    if not success:
        break

    frame_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = pose.process(frame_rgb)

    if result.pose_landmarks:
        mp_drawing.draw_landmarks(img, result.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        # Get coordinates of shoulders (landmarks 11 and 12)
        landmarks = result.pose_landmarks.landmark
        shoulder_left = [landmarks[11].x * img.shape[1], landmarks[11].y * img.shape[0]]
        shoulder_right = [landmarks[12].x * img.shape[1], landmarks[12].y * img.shape[0]]
        center_x = int((shoulder_left[0] + shoulder_right[0]) / 2)
        center_y = int((shoulder_left[1] + shoulder_right[1]) / 2)
        current_center = (center_x, center_y)
        current_time = time.time()

        speed, direction = calculate_speed_and_direction(current_center, previous_center, current_time, previous_time)

        previous_center = current_center 
        previous_time = current_time

        
        cv2.circle(img, current_center, 5, (0, 255, 0), -1)
        cv2.putText(img, f"Speed: {speed:.2f} m/s", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(img, f"X Direction: {direction}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        

        # Send the speed and direction to the Arduino
        try:
            arduino.write(f"{speed:.2f},{direction}\n".encode())
        except serial.SerialException as e:
            print(f"Failed to write to serial port: {e}")
    else:
        direction = "No one"
        cv2.putText(img, f"X Direction: {direction}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        try:
            arduino.write(f"{direction}\n".encode())
        except serial.SerialException as e:
            print(f"Failed to write to serial port: {e}")
            
    cv2.imshow('Video', img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
arduino.close()