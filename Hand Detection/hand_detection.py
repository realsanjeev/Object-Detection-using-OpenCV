import cv2
from hand_detector import HandDetector

capture = cv2.VideoCapture(0)
hand_detector = HandDetector()

def main():
    while True:
        success, frame = capture.read()
        
        if not success:
            break
        
        detect = hand_detector.find_hand(frame)
        pos = hand_detector.find_position(frame)
        
        # Check if positions are detected and print the first hand's landmarks
        if len(pos) > 0:
            for hand_id, hand_position in enumerate(pos):
                print(f"Hand {hand_id}: Landmark ID {hand_position[0]}, x: {hand_position[1]}, y: {hand_position[2]}")
        
        cv2.imshow("Live Capture", detect)
        
        # Exit if 'q' is pressed
        if cv2.waitKey(20) & 0xFF == ord('q'):
            break

    capture.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
