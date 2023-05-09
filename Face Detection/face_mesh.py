import cv2
import time
import mediapipe as mp

class FaceMesh():
    def __init__(self, mode=False, max_face=1, 
                 refine_landmarks=False, 
                 detect_confidence=0.5, track_confidence=0.5) -> None:
        self.mode = mode
        self.max_face = max_face
        self.refine_landmarks = refine_landmarks
        self.detect_confidence = detect_confidence
        self.track_confidence = track_confidence

        self.mp_draws = mp.solutions.drawing_utils
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(static_image_mode=self.mode,
                                                max_num_faces=self.max_face,
                                                refine_landmarks=self.refine_landmarks,
                                                min_detection_confidence=self.detect_confidence,
                                                min_tracking_confidence=self.track_confidence)

    def draw_mesh(self, image, thickness=1, circle_radius=1, color=(0,255, 0)):
        draw_spec = self.mp_draws.DrawingSpec(thickness=thickness, circle_radius=circle_radius, color=color)
        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(img_rgb)
        lst_mark = list()

        if results.multi_face_landmarks:
            h, w, c = image.shape
            for face_id, landmarks in enumerate(results.multi_face_landmarks):
                self.mp_draws.draw_landmarks(image, landmarks, 
                                             self.mp_face_mesh.FACEMESH_FACE_OVAL, draw_spec)
                for id,mark in enumerate(landmarks.landmark):
                    cx, cy = mark.x, mark.y
                    lst_mark.append([face_id, id, cx, cy])

        return lst_mark


def main():
    capture = cv2.VideoCapture(0)
    face_mesh = FaceMesh()
    prev_time = 0
    while True:
        sucess, frame = capture.read()
        lst_position = face_mesh.draw_mesh(frame)
        if len(lst_position) != 0:
            print(lst_position[0])

        # calculate fps
        current_time = time.time()
        fps = 1 / (current_time - prev_time)
        prev_time = current_time

        # put fps of video in display
        cv2.putText(frame,  f"{str(int(fps))}", (19, 50), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 255), thickness=2)

        # display video window
        cv2.imshow("Video Display", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
