import cv2
for i in range(10):
    cap = cv2.VideoCapture(i)
    if cap is None or not cap.isOpened():
        print('Warning: unable to open video source: ', i)
    else:
        print('Success: able to open video source: ', i)
cap.release()
