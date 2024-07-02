import cv2
import mediapipe as mp
import time
import PoseModule as pm
import win32com.client as comclt
import numpy as np

cap = cv2.VideoCapture(0)
pTime = 0
detector = pm.poseDetector()

previous_center = None
previous_time = None

while True:
    success, img = cap.read()
    img = detector.findPose(img)
    lmList = detector.findPosition(img, draw=False)

    if len(lmList) > 0:
        # Calculate the midpoint between shoulders (landmarks 11 and 12)
        center = (
            (lmList[11][1] + lmList[12][1]) // 2,
            (lmList[11][2] + lmList[12][2]) // 2
        )

        if previous_center is not None:
            pixel_distance = np.linalg.norm(np.array(center) - np.array(previous_center))
            current_time = time.time()
            time_elapsed = current_time - previous_time
            speed_pxs = pixel_distance / time_elapsed
             
            speed_mps = speed_pxs * 0.01
            
            # Determine direction
            if center[0] > previous_center[0]:
                direction = "Right"
            elif center[0] < previous_center[0]:
                direction = "Left"
            else: 
                direction = "Still"
            
            # Display speed and direction on frame
            cv2.putText(img, f"Speed: {speed_mps:.2f} m/s", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(img, f"Direction: {direction}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        
        previous_center = center
        previous_time = time.time()

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    
    # Add FPS to the image
    cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 255, 0), 2)
    
    cv2.imshow("Video", img)
    if cv2.waitKey(1) == ord('q'):
        break

# transmit it to the arduino


cap.release()
cv2.destroyAllWindows()