import cv2
import time
import numpy as np
from hand_detector import HandDetector

# Load menu image
menu = cv2.imread("menu.png")

# Set up video capture
capture = cv2.VideoCapture(0)
WIDTH, HEIGHT = int(capture.get(3)), int(capture.get(4))
draw_canvas = np.zeros((HEIGHT, WIDTH, 3), dtype="uint8")
print(f"[INFO] Shape of live video: {HEIGHT} X {WIDTH}")

# Resize menu image to match video dimensions
menu = cv2.resize(menu, (WIDTH, menu.shape[0]))
print(f"[INFO] Shape of menu: {menu.shape}")

# Initialize hand detector
detect = HandDetector(detect_confidence=0.7, track_confidence=0.4)
prev_time = 0

xp = None
PAINT_COLOR = (0, 255, 0)

while True:
    # Capture frame from video
    success, frame = capture.read()
    frame = cv2.flip(frame, 1)

    # Find hand in the frame
    detect.find_hand(frame)

    # Find hand landmarks
    lst_mark = detect.find_position(frame)

    if len(lst_mark) != 0:
        # Get tip of index finger position
        x1, y1 = int(lst_mark[8][1] * WIDTH), int(lst_mark[8][2] * HEIGHT)
        x2, y2 = int(lst_mark[12][1] * WIDTH), int(lst_mark[12][2] * HEIGHT)

        # Determine finger up configuration
        up_finger = detect.fingerUp(lst_mark)
        # print(up_finger)
        count = up_finger.count(1)

        # Set mode based on finger configuration
        if count == 1 and up_finger[1] == 1:  # Index finger up
            mode = "DRAWING"
        elif count >= 2:
            mode = "SELECTION"
        else:
            mode = "IDEAL"

        if mode == "SELECTION":
            xp = None
            print(f"[INFO] Selection mode")
            if x1 <= 128 and y1 <= 80:
                print("--------------")
                instruction = f"""
                PAINTER INSTRUCTIONS:
                Index finger up: DRAWING mode
                2 fingers up: SELECTION mode for painting options
                Other hand configurations: IDEAL mode
                """
                line_spacing = 30  # Adjust the spacing between lines
                y = 90  # Initial y-coordinate for the first line

                lines = instruction.split('\n')
                for line in lines:
                    cv2.putText(frame, line, (10, y), cv2.FONT_HERSHEY_PLAIN,
                                1.2, (255, 255, 255), 2)
                    y += line_spacing
            elif x1 <= 256 and y1 <= 80:
                PAINT_COLOR = (0, 255, 0)
            elif x1 <= 384 and y1 <= 80:
                PAINT_COLOR = (0, 0, 255)
            elif x1 <= 512 and y1 <= 80:
                PAINT_COLOR = (255, 0, 0)
            elif x1 <= 640 and y1 <= 80:
                PAINT_COLOR = (0, 0, 0)

        elif mode == "DRAWING":
            print("[INFO] Drawing mode")
            if xp is None:
                xp, yp = x1, y1
            cv2.line(draw_canvas, (xp, yp), (x1, y1), PAINT_COLOR, thickness=4)
            xp, yp = x1, y1
        else:
            xp = None
    
    # Threshold the drawing canvas to create a black-and-white image for blending
    thres, thres_image = cv2.threshold(draw_canvas, 128, 255, cv2.THRESH_BINARY_INV)
    
    # Merge the drawing canvas with the video frame
    frame = cv2.bitwise_and(frame, thres_image)
    frame = cv2.bitwise_or(frame, draw_canvas)

    # Overlay menu image on top of the video frame
    frame[0:menu.shape[0], 0:WIDTH] = menu
    
    # Calculate and display FPS
    current_time = time.time()
    fps = 1 / (current_time - prev_time)
    prev_time = current_time
    cv2.putText(frame, f"FPS: {int(fps)}", (0, HEIGHT - 30), 
                cv2.FONT_HERSHEY_PLAIN, 1.3, (155, 89, 255), 1)

    # Display the selected painting color
    cv2.putText(frame, "Color", (0, 20), cv2.FONT_HERSHEY_PLAIN, 1.4, (255, 255, 255), thickness=2)
    cv2.rectangle(frame, (70, 0), (95, 20), PAINT_COLOR, -1)

    # Display the video frame
    cv2.imshow("Drawing in screen", frame)
    # Uncomment to see the drawing screen separately
    # cv2.imshow("DrawCanvas", draw_canvas)

    # Check for 'q' key press to exit the loop
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release video capture and close windows
capture.release()
cv2.destroyAllWindows()
