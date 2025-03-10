import cv2
import time
import mediapipe as mp

class FaceMesh:
    def __init__(self, static_image_mode=False, max_num_faces=1, 
                 refine_landmarks=False, 
                 min_detection_confidence=0.5, min_tracking_confidence=0.5) -> None:
        self.static_image_mode = static_image_mode
        self.max_num_faces = max_num_faces
        self.refine_landmarks = refine_landmarks
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence

        self.mp_draws = mp.solutions.drawing_utils
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=self.static_image_mode,
            max_num_faces=self.max_num_faces,
            refine_landmarks=self.refine_landmarks,
            min_detection_confidence=self.min_detection_confidence,
            min_tracking_confidence=self.min_tracking_confidence
        )

    def draw_mesh(self, image, thickness=1, circle_radius=1, color=(0, 255, 0)):
        draw_spec = self.mp_draws.DrawingSpec(thickness=thickness, circle_radius=circle_radius, color=color)
        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(img_rgb)
        landmarks_list = []

        if results.multi_face_landmarks:
            h, w, c = image.shape
            for face_id, landmarks in enumerate(results.multi_face_landmarks):
                # Draw the mesh with the oval connections for the face
                self.mp_draws.draw_landmarks(image, landmarks, 
                                             self.mp_face_mesh.FACEMESH_FACE_OVAL, draw_spec)
                # Store landmarks coordinates in a list
                for id, mark in enumerate(landmarks.landmark):
                    cx, cy = int(mark.x * w), int(mark.y * h)
                    landmarks_list.append([face_id, id, cx, cy])

        return landmarks_list


def main():
    capture = cv2.VideoCapture(0)
    face_mesh = FaceMesh()
    prev_time = 0
    fps_list = []  # To average FPS

    while True:
        success, frame = capture.read()
        if not success:
            break
        
        landmarks_list = face_mesh.draw_mesh(frame)

        # Calculate FPS
        current_time = time.time()
        fps = 1 / (current_time - prev_time)
        prev_time = current_time
        
        # Averaging FPS over multiple frames for stability
        fps_list.append(fps)
        if len(fps_list) > 10:  # Keep the last 10 FPS values
            fps_list.pop(0)
        
        avg_fps = int(sum(fps_list) / len(fps_list))  # Calculate average FPS
        
        # Display the FPS on the video
        cv2.putText(frame, f"FPS: {avg_fps}", (19, 50),
                    cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 255), thickness=2)

        # Display video window with the face mesh drawn on it
        cv2.imshow("Video Display", frame)
        
        # Exit the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
