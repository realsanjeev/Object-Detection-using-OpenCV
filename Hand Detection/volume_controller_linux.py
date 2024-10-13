'''
For linux we can use amixer to control the volume

sudo apt install alsa-utils
'''
import os
import time
import math
import cv2
import numpy as np

from hand_detector import HandDetector

# Initialize hand detector and camera capture
capture = cv2.VideoCapture(0)
detector = HandDetector(0.7)

# Constants for thumb and index finger tips
THUMB_TIP = 4
INDEX_FINGER_TIP = 8

# Minimum and maximum distances for volume control
MIN_VOL_DISTANCE = 19
MAX_VOL_DISTANCE = 122
prev_time = 0

def draw_focus(image, x1, y1, x2, y2, volume):
    # Draw a line between the thumb and index finger tips
    cv2.line(image, (x1, y1), (x2, y2), (255, 255, 0), 3)

    # Draw circles at the tips
    cv2.circle(image, (x1, y1), 10, (255, 0, 255), -1)
    cv2.circle(image, (x2, y2), 10, (255, 0, 255), -1)

    # Display the volume percentage
    cv2.putText(image, f"VOL: {int(volume)} %", (10, 90), cv2.FONT_HERSHEY_PLAIN, 1.3, (155, 155, 255), 3)

    # Draw volume showcase
    cv2.rectangle(image, (10, 100), (40, 300), (0, 0, 255), 1)
    y_vol = int(np.interp(volume, [0, 100], [300, 100]))
    cv2.rectangle(image, (10, y_vol), (40, 300), (0, 255, 0), -1)

while True:
    success, frame = capture.read()
    if not success:
        print("[ERROR] Failed to capture frame.")
        break

    # Detect hand in the current frame
    detector.find_hand(frame)

    # Get the landmarks of the hand if detected
    list_mark = detector.find_position(frame)

    # If landmarks for the hand are detected
    if len(list_mark) != 0:
        h, w, c = frame.shape
        x1, y1 = int(list_mark[THUMB_TIP][1] * w), int(list_mark[THUMB_TIP][2] * h)
        x2, y2 = int(list_mark[INDEX_FINGER_TIP][1] * w), int(list_mark[INDEX_FINGER_TIP][2] * h)
        distance = int(math.hypot((x2 - x1), (y2 - y1)))

        # Map the distance to volume control range
        dist_to_vol = np.interp(distance, [MIN_VOL_DISTANCE, MAX_VOL_DISTANCE], [0, 100])

        # Set the volume using amixer
        os.system(f'amixer -D pulse sset Master {dist_to_vol}%')

        # Draw a circle at the tips and display volume percentage
        draw_focus(frame, x1, y1, x2, y2, volume=dist_to_vol)

    # Calculate and display FPS
    current_time = time.time()
    fps = 1 / (current_time - prev_time)
    prev_time = current_time
    cv2.putText(frame, f"FPS: {int(fps)}", (10, 40), cv2.FONT_HERSHEY_PLAIN, 1.2, (0, 255, 255), 1)

    # Display the frame in a window
    cv2.imshow("Volume Control", frame)

    # Exit on 'q' key press
    if cv2.waitKey(20) & 0xFF == ord('q'):
        break

capture.release()
cv2.destroyAllWindows()
