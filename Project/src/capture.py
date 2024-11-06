import cv2
import os

# Initialize video capture from the default camera
def capture_frame():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture image.")
        cap.release()
        return None
    return frame

def save_image(image, path):
    cv2.imwrite(path, image)
