import mediapipe as mp
import cv2

class HandDetector():
    """
    A class to detect hands in images or videos using the MediaPipe Hands library.
    
    Args:
    - static_mode (bool): If True, detects hands only on the first input image/frame. Defaults to False.
    - max_hands (int): Maximum number of hands to detect. Defaults to 2.
    - model_complexity (int): Complexity of the detection model, ranges from 0 to 2. Defaults to 1.
    - detect_confidence (float): Minimum confidence value for detection to be considered successful. 
                                Ranges from 0 to 1. Defaults to 0.5.
    - track_confidence (float): Minimum confidence value for tracking to be considered successful. 
                                Ranges from 0 to 1. Defaults to 0.5.

    Attributes:
    - FINGER_TIP (list): Indexes of the hand landmarks corresponding to the fingertips.
    - mp_hands: MediaPipe Hands object for detecting hands.
    - hands: A MediaPipe Hands model instance with the specified configurations.
    - mp_draw: MediaPipe drawing utilities for drawing hand landmarks and connections on the image.

    """
    def __init__(self, static_mode=False, max_hands=2,
                 model_complexity=1, 
                 detect_confidence=0.5, 
                 track_confidence=0.5) -> None:
        
        self.static_mode = static_mode
        self.max_hands = max_hands
        self.model_complexity = model_complexity
        self.detect_confidence = detect_confidence
        self.track_confidence = track_confidence

        self.FINGER_TIP = [4, 8, 12, 16, 20]

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
        finger_status = list()

        # Thumb: Compare landmark 4 and landmark 3 (y-axis)
        if lst_mark[4][1] < lst_mark[3][1]:
            finger_status.append(1)
        else:
            finger_status.append(0)

        # For the rest of the fingers, compare the fingertip with the previous joint
        # Starting from index 8, 12, 16, 20
        for id in self.FINGER_TIP[1:]:
            # Check if the tip is above the previous joint (y-axis)
            if lst_mark[id][2] < lst_mark[id - 1][2]:
                finger_status.append(1)
            else:
                finger_status.append(0)

        return finger_status
