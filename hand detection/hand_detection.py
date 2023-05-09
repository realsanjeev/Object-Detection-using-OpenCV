import cv2
from hand_detector import HandDetector

capture = cv2.VideoCapture(0)
hand_detector = HandDetector()
while True:
    sucess, frame = capture.read()
    
    detect = hand_detector.find_hand(frame)
    pos = hand_detector.find_position(frame)
    if len(pos) != 0:
        print(pos[1])

    cv2.imshow("Live Capture", detect)
    if cv2.waitKey(20) & 0xFF == ord('q'):
        break

capture.release()
cv2.destroyAllWindows()

if '__name__' == '__main__':
    main()