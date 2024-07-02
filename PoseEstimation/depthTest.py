import cv2
import mediapipe as mp
import time
import numpy as np

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

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
        if len(landmarks) > 12:
            shoulder_left = [landmarks[11].x * img.shape[1], landmarks[11].y * img.shape[0], landmarks[11].z]
            shoulder_right = [landmarks[12].x * img.shape[1], landmarks[12].y * img.shape[0], landmarks[12].z]
            center_x = int((shoulder_left[0] + shoulder_right[0]) / 2)
            center_y = int((shoulder_left[1] + shoulder_right[1]) / 2)
            center_z = (shoulder_left[2] + shoulder_right[2]) / 2

            cv2.circle(img, (center_x, center_y), 5, (0, 255, 0), -1)
            cv2.putText(img, f"X Coordinate: {center_x}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(img, f"Z Coordinate: {center_z:.2f}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        else:
            print("Insufficient landmarks detected")
    else:
        cv2.putText(img, "No person detected", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
       
    cv2.imshow('Video', img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
