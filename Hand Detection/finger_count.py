import cv2
import time
from hand_detector import HandDetector

def draw_count(image, count, width, height):
    print(type(width))
    cv2.rectangle(image, (500, 300), (width, height), (0, 155, 155), -1)
    cv2.putText(image, f"{count}", (550, 350), cv2.FONT_HERSHEY_PLAIN, 3, (155, 0, 155), 3)

def main():
    WIDTH = 700
    HEIGHT = 200

    capture = cv2.VideoCapture(0)
    detect = HandDetector()
    # sset resolution
    capture.set(3, WIDTH)
    capture.set(4, HEIGHT)

    # resolution ay be different. Actual resolution
    ACTUAL_WIDTH = int(capture.get(3))
    ACTUAL_HEIGHT = int(capture.get(4))
    print(f"[INFO] Resolution of image(w x h): {ACTUAL_WIDTH} x {ACTUAL_HEIGHT}")
    prev_time = 0
    while True:
        success, frame = capture.read()
        frame = cv2.flip(frame, 1)
        detect.find_hand(frame)

        lst_mark = detect.find_position(frame)
        if len(lst_mark) != 0:
            up_fingure = detect.fingerUp(lst_mark)
            print(up_fingure)
            count = up_fingure.count(1)
            draw_count(frame, count, ACTUAL_WIDTH, ACTUAL_HEIGHT)

        current_time = time.time()
        fps = 1 / (current_time - prev_time)
        prev_time = current_time
        cv2.putText(frame, f"FPS: {int(fps)}", (10, 20), cv2.FONT_HERSHEY_PLAIN, 1.6, (155, 155, 155), 1)

        cv2.imshow("Finger Counting", frame)
        if cv2.waitKey(20) & 0xFF == ord("q"):
            break

    capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()