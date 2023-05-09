import cv2
import time
import math
import numpy as np
from hand_detector import HandDetector

from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
volume.GetMute()
volume.GetMasterVolumeLevel()
VOL_RANGE = volume.GetVolumeRange()

MIN_VOLUME = VOL_RANGE[0]
MAX_VOLUME = VOL_RANGE[1]
print(F"[INFO] Voltage range setting: {VOL_RANGE}")

detector = HandDetector(0.7)
capture  = cv2.VideoCapture(0)

# MARKING INDEX FOR THUMP_TIP AND INDEX_FINGER_TIP
THUMP_TIP = 4
INDEX_FINGER_TIP = 8
# MINIMUM AND MAXIMUM DISTANCE FOR VOLUME CONTROL
MIN_VOL_DISTANCE = 19
MAX_VOL_DISTANCE = 122
prev_time = 0

def draw_focus(image, x1, y1, x2, y2, volume):
    # connect the tip
    cv2.line(image, (x1, y1), (x2, y2), (255, 255, 0), 3)

    # focus in tip
    cv2.circle(image, (x1, y1), 10, (255, 0, 255), -1)
    cv2.circle(image, (x2, y2), 10, (255, 0, 255), -1)

    # show volumw
    cv2.putText(image, f"VOL: {int(volume)} %", (10, 90), cv2.FONT_HERSHEY_PLAIN, 1.3, (155,155, 255), 3)

    # draw the volumeshowcase
    cv2.rectangle(image, (10, 100), (40, 300), (0, 0, 255), 1)
    # draw volume range
    y_vol = int(np.interp(volume, [0, 100], [300, 100]))
    cv2.rectangle(image, (10, y_vol), (40, 300), (0, 255, 0), -1)


while True:
    sucess, frame = capture.read()
    detector.find_hand(frame)
    list_mark = detector.find_position(frame)
    if len(list_mark) != 0:
        h, w, c = frame.shape
        x1, y1 = int(list_mark[THUMP_TIP][1] * w), int(list_mark[THUMP_TIP][2] * h)
        x2, y2 = int(list_mark[INDEX_FINGER_TIP][1] * w), int(list_mark[INDEX_FINGER_TIP][2] * h)
        distance = int(math.hypot((x2-x1), (y2-y1)))

        dist_to_vol = np.interp(distance, 
                                [MIN_VOL_DISTANCE, MAX_VOL_DISTANCE], 
                                [MIN_VOLUME, MAX_VOLUME])
        # print(distance)
        volume.SetMasterVolumeLevel(dist_to_vol, None)

        volume_percent = np.interp(dist_to_vol, [MIN_VOLUME, MAX_VOLUME], [0, 100])

        draw_focus(frame, x1, y1, x2, y2, volume=volume_percent)  

    current_time = time.time()
    fps = 1 / (current_time - prev_time)
    prev_time = current_time
    cv2.putText(frame, f"FPS: {int(fps)}", (10, 40),
                cv2.FONT_HERSHEY_PLAIN,
                1.2, (0, 255, 255), 1)
    
    cv2.imshow("Volume Control", frame)
    # cv2.waitKey(1)
    if cv2.waitKey(20) & 0xFF == ord('q'):
        break

capture.release()
cv2.destroyAllWindows()