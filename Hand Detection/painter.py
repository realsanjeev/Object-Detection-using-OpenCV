import cv2
import  time
import numpy as np
from hand_detector import HandDetector

capture = cv2.VideoCapture(0)
WIDTH, HEIGHT = int(capture.get(3)), int(capture.get(4))
draw_canvas = np.zeros((HEIGHT, WIDTH), dtype="uint8")

detect = HandDetector()
prev_time = 0

while True:
    sucess, frame = capture.read()
    frame = cv2.flip(frame, 1)
    detect.find_hand(frame)
    lst_mark = detect.find_position(frame)
    if len(lst_mark) != 0:
        # print(lst_mark[4])
        # tip index position in up condition
        x1, y1 =  int(lst_mark[4][1] * WIDTH), int(lst_mark[4][1] * HEIGHT)
        cv2.circle(draw_canvas, (x1, y1), 5, (255, 0, 255), -1)

    # calculate and dispkay fps
    current_time = time.time()
    fps = 1 / (current_time - prev_time)
    prev_time = current_time
    cv2.putText(frame, f"FPS: {int(fps)}", (10, 20), 
                cv2.FONT_HERSHEY_PLAIN, 1.3, (155, 89, 255),1)

    # view video
    cv2.imshow("Drawing in screen", frame)
    cv2.imshow("DrawCanvas", draw_canvas)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

capture.release()
cv2.destroyAllWindows()
