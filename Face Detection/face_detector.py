import cv2
import time
import mediapipe as mp

class FaceDetector():
    def __init__(self, confidence=0.5, model=0) -> None:
        self.confidence = confidence
        self.model = model

        self.mp_draws = mp.solutions.drawing_utils
        self.mp_faces = mp.solutions.face_detection
        self.faces = self.mp_faces.FaceDetection(min_detection_confidence=confidence, model_selection=model)

    def face_detection(self, image, draw=True, position=False):
        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.faces.process(image)
        lst_box = list()

        if results.detections:
            if draw:
                for id, detection in enumerate(results.detections):
                    h, w, c = image.shape

                    r_bbox = detection.location_data.relative_bounding_box
                    print("-"*20)
                    bbox = int(r_bbox.xmin * w), int(r_bbox.ymin * h), \
                            int(r_bbox.width * w), int(r_bbox.height * h)
                    score = detection.score

                    print(bbox)
                    lst_box.append([id, bbox, score])
                    self.draw_box_detection(image, bbox, score)
                    # self.mp_draws.draw_detection(image, detection)
        return lst_box

    def draw_box_detection(self, image, bbox, score):
        xmin, ymin = bbox[0], bbox[1]
        h, w, c = image.shape
        l = 30

        cv2.rectangle(image, bbox, color=(255, 0, 255),  thickness=1)
        cv2.line(image, (xmin, ymin), (xmin+l, ymin), (255, 0, 255), thickness=5)
        cv2.line(image, (xmin, ymin), (xmin, ymin+l), (255, 0, 255), thickness=5)
        cv2.putText(image, f"{str(int(score[0] * 100))}%", (xmin, ymin - 10), 
                    cv2.FONT_HERSHEY_PLAIN, fontScale=1.3, 
                    color=(0, 255,0), thickness=1)


def main():
    capture = cv2.VideoCapture(0)
    face_detector = FaceDetector()
    prev_time = 0
    while True:
        sucess, frame = capture.read()
        lst_position = face_detector.face_detection(frame)
        if len(lst_position) != 0:
            print(lst_position[0])

        # calculate fps
        current_time = time.time()
        fps = 1 / (current_time - prev_time)
        prev_time = current_time

        # put fps of video in display
        cv2.putText(frame,  f"{str(int(fps))}", (19, 50),
                    cv2.FONT_HERSHEY_PLAIN, 1.5, 
                    (0, 255, 255), thickness=2)

        # display video window
        cv2.imshow("Video Display", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
