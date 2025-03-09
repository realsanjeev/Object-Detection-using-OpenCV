import cv2
import mediapipe as mp
import time

class PoseDetector():
    def __init__(self, mode=False, complexity=1, smooth_landmarks=True,  
                 enable_segmentation=False, smooth_segmentation=True, 
                 detection_confidence=0.5, tracking_confidence=0.5) -> None:
        self.mode = mode
        self.complexity = complexity
        self.smooth_landmarks = smooth_landmarks
        self.enable_segmentation = enable_segmentation
        self.smooth_segmentations = smooth_segmentation
        self.detection_confidence = detection_confidence
        self.tracking_confidence = tracking_confidence

        self.mp_pose = mp.solutions.pose
        self.mp_draw = mp.solutions.drawing_utils
        self.poses = self.mp_pose.Pose(static_image_mode=self.mode,
                                  model_complexity=self.complexity, 
                                  smooth_landmarks=self.smooth_landmarks, 
                                  enable_segmentation=self.enable_segmentation, 
                                  smooth_segmentation=self.smooth_segmentations, 
                                  min_detection_confidence=self.detection_confidence, 
                                  min_tracking_confidence=self.tracking_confidence
                                  )
        
        
    def findPose(self, image, draw=True, position_mark=False):
        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.poses.process(img_rgb)
        lst_mark_position = list()
        if results.pose_landmarks:
            if draw:
                self.mp_draw.draw_landmarks(image, results.pose_landmarks, 
                                            self.mp_pose.POSE_CONNECTIONS)
        
            if position_mark:
                for id, mark in enumerate(results.pose_landmarks.landmark):
                    h, w, c = image.shape
                    cx, cy = int(mark.x * w), int(mark.y * h)
                    lst_mark_position.append([id, cx, cy])
        return lst_mark_position

def main():
    capture = cv2.VideoCapture(0)
    prev_time = 0 
    pose_detector = PoseDetector()
    while True:
        success, frame = capture.read()
        if not success:
            break
            
        lst = pose_detector.findPose(frame)
        if len(lst) != 0:
            print(lst[3])
        

        current_time = time.time()
        frame_rate = 1 / (current_time - prev_time)
        prev_time = current_time
        cv2.putText(frame, text=str(int(frame_rate)), org=(10, 30), 
                    fontFace=cv2.FONT_HERSHEY_PLAIN, fontScale=1.3, 
                    color=(255, 255, 0), thickness=1)
        cv2.imshow("Video", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()