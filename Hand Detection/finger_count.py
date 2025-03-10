import time
import cv2
import numpy as np

from hand_detector import HandDetector

def draw_count(image: np.ndarray, count: int, width: int, height: int):
    # Calculate rectangle coordinates
    start_x = int(width * 0.85)
    start_y = int(height * 0.85)
    end_x = width
    end_y = height
    
    # Draw rectangle (fill with color (155, 155, 155) and thickness -1 to fill it)
    cv2.rectangle(image, (start_x, start_y), (end_x, end_y), (155, 155, 155), -1)
    
    # Position text near the bottom-right corner, with dynamic spacing
    text = f"{count}"
    font = cv2.FONT_HERSHEY_PLAIN
    font_scale = 4
    font_thickness = 3
    text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
    
    # 10px padding from the edge and bottom
    text_x = width - text_size[0] - 10
    text_y = height - 10
    
    # Put text on image
    cv2.putText(image, text, (text_x, text_y), font, font_scale, (155, 0, 155), font_thickness)


def main():
    WIDTH = 700
    HEIGHT = 200

    capture = cv2.VideoCapture(0)
    detect = HandDetector()
    # Set resolution
    capture.set(3, WIDTH)
    capture.set(4, HEIGHT)

    # Get the actual resolution from the camera
    ACTUAL_WIDTH = int(capture.get(3))
    ACTUAL_HEIGHT = int(capture.get(4))
    print(f"[INFO] Resolution of image(w x h): {ACTUAL_WIDTH} x {ACTUAL_HEIGHT}")
    prev_time = 0
    
    while True:
        success, frame = capture.read()
        if not success:
            break

        # Flip the frame for mirroring
        frame = cv2.flip(frame, 1)
        detect.find_hand(frame)

        lst_mark = detect.find_position(frame)
        
        if len(lst_mark) != 0:
            up_finger = detect.fingerUp(lst_mark)
            count = up_finger.count(1)
            draw_count(frame, count, ACTUAL_WIDTH, ACTUAL_HEIGHT)

        # FPS calculation
        current_time = time.time()
        fps = 1 / (current_time - prev_time)
        prev_time = current_time
        cv2.putText(frame, f"FPS: {int(fps)}", (10, 20), 
                    cv2.FONT_HERSHEY_PLAIN, 1.6, (155, 155, 255), 1)
        
        # Show the video
        cv2.imshow("Finger Counting", frame)
        
        # Exit loop on pressing 'q'
        if cv2.waitKey(20) & 0xFF == ord("q"):
            break

    capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()