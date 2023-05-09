import mediapipe as mp
import cv2

class HandDetector():
    def __init__(self, static_mode=False, max_hands=2,
                 model_complextiy=1, 
                 detect_confidence=0.5, 
                 track_confidence=0.5) -> None:
        
        self.static_mode = static_mode
        self.max_hands = max_hands
        self.model_complexity = model_complextiy
        self.detect_confidence = detect_confidence
        self.track_confidence = track_confidence

        self.FINGURE_TIP = [4, 8, 12, 16, 20]

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(static_image_mode=self.static_mode, 
                                         max_num_hands=self.max_hands, 
                                         model_complexity=self.model_complexity, 
                                         min_detection_confidence=self.detect_confidence,
                                         min_tracking_confidence=self.track_confidence)

        self.mp_draw = mp.solutions.drawing_utils
    
    def find_hand(self, image, draw=True):
        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)
        if self.results.multi_hand_landmarks:
            if draw:
                for hand in self.results.multi_hand_landmarks:
                    # print(hand)
                    self.mp_draw.draw_landmarks(image, hand, self.mp_hands.HAND_CONNECTIONS)
        return image
    
    def find_position(self, image):
        h, w, c = image.shape
        lst_position = []
        if self.results.multi_hand_landmarks:
            for hand in self.results.multi_hand_landmarks:
                for id, mark in enumerate(hand.landmark):
                    # cx, cy = int(mark.x * w), int(mark.y * h)
                    lst_position.append([id, mark.x, mark.y])
        return lst_position
    
    def fingerUp(self, lst_mark):
        fingure_status = list()
        # for right hand thumb
        if lst_mark[4][1] < lst_mark[4 -1][1]:
            fingure_status.append(1)
        else:
            fingure_status.append(0)
        for id in self.FINGURE_TIP[1:]:
            if lst_mark[id][2] < lst_mark[id -1][2]:
                fingure_status.append(1)
            else:
                fingure_status.append(0)
        return fingure_status