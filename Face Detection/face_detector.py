import time
import cv2
import mediapipe as mp

class FaceDetector():
    def __init__(self, min_detection_confidence=0.5, model_selection=0) -> None:
        self.min_detection_confidence = min_detection_confidence
        self.model_selection = model_selection

        self.mp_draws = mp.solutions.drawing_utils
        self.mp_faces = mp.solutions.face_detection
        self.faces = self.mp_faces.FaceDetection(
            min_detection_confidence=min_detection_confidence, 
            model_selection=model_selection
        )

    def face_detection(self, image, draw=True):
        # Convert the image to RGB (MediaPipe works with RGB images)
        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.faces.process(img_rgb)
        lst_box = list()

        if results.detections:
            for id, detection in enumerate(results.detections):
                h, w, c = image.shape

                r_bbox = detection.location_data.relative_bounding_box
                bbox = int(r_bbox.xmin * w), int(r_bbox.ymin * h), \
                        int(r_bbox.width * w), int(r_bbox.height * h)
                score = detection.score
                lst_box.append([id, bbox, score])
                
                if draw:
                    self.draw_box_detection(image, bbox, score)
                    # self.mp_draws.draw_detection(image, detection)
        return lst_box

    def draw_box_detection(self, image, bbox, score):
        xmin, ymin = bbox[0], bbox[1]
        h, w, c = image.shape
        # Length for the lines drawn on the bounding box corners
        l = 30

        # Draw rectangle around the detected face
        cv2.rectangle(image, bbox, color=(255, 0, 255), thickness=2)
        
        # Draw lines at the top-left corner
        cv2.line(image, (xmin, ymin), (xmin+l, ymin), (255, 0, 255), thickness=5)
        cv2.line(image, (xmin, ymin), (xmin, ymin+l), (255, 0, 255), thickness=5)
        
        # Display the score of detection near the box
        cv2.putText(image, f"{str(int(score[0] * 100))}%", (xmin, ymin - 10), 
                    cv2.FONT_HERSHEY_PLAIN, fontScale=1.3, 
                    color=(0, 255, 0), thickness=2)

def main():
    capture = cv2.VideoCapture(0)
    face_detector = FaceDetector()
    prev_time = 0
    fps_list = []  # For averaging FPS

    while True:
        success, frame = capture.read()
        if not success:
            break

        # Detect faces in the frame
        lst_position = face_detector.face_detection(frame)
        if len(lst_position) != 0:
            print(lst_position[0])

        # Calculate FPS
        current_time = time.time()
        fps = 1 / (current_time - prev_time)
        prev_time = current_time
        
        # Store FPS values for averaging
        fps_list.append(fps)
        if len(fps_list) > 10:
            fps_list.pop(0)
        
        avg_fps = int(sum(fps_list) / len(fps_list))  # Calculate average FPS
        
        # Display FPS on the video feed
        cv2.putText(frame, f"FPS: {avg_fps}", (19, 50),
                    cv2.FONT_HERSHEY_PLAIN, 1.5, 
                    (0, 255, 255), thickness=2)

        # Display video window
        cv2.imshow("Video Display", frame)
        
        # Exit the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
