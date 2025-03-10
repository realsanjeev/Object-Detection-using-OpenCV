"""
Robust Finger Counting Application
Works with various hand orientations and positions
"""
import time
import cv2
import numpy as np
from hand_detector import HandDetector


class FingerCounter:
    """Robust finger counting with multi-orientation support."""
    
    def __init__(self):
        """Initialize the finger counter."""
        self.detector = HandDetector(detect_confidence=0.75, track_confidence=0.5)
        self.finger_tips = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky
        self.finger_pips = [2, 6, 10, 14, 18]  # PIP joints (one below tip)
        
    def is_hand_vertical(self, landmarks):
        """
        Determine if hand is vertical (palm facing camera) or horizontal.
        
        Args:
            landmarks: Hand landmarks
            
        Returns:
            bool: True if hand is vertical
        """
        # Compare wrist (0) to middle finger MCP (9)
        wrist_y = landmarks[0][2]
        middle_mcp_y = landmarks[9][2]
        
        # If middle MCP is significantly above wrist, hand is vertical
        return abs(middle_mcp_y - wrist_y) > 0.1
    
    def get_hand_orientation(self, landmarks):
        """
        Determine hand orientation (left/right).
        
        Args:
            landmarks: Hand landmarks
            
        Returns:
            str: 'left' or 'right'
        """
        # Compare thumb and pinky positions
        thumb_x = landmarks[4][1]
        pinky_x = landmarks[20][1]
        
        # If thumb is to the left of pinky, it's a right hand (in mirror view)
        return 'right' if thumb_x < pinky_x else 'left'
    
    def count_fingers_robust(self, landmarks):
        """
        Count fingers with robust orientation handling.
        
        Args:
            landmarks: Hand landmarks
            
        Returns:
            int: Number of fingers up
        """
        if len(landmarks) == 0:
            return 0
        
        fingers_up = []
        orientation = self.get_hand_orientation(landmarks)
        is_vertical = self.is_hand_vertical(landmarks)
        
        # Thumb detection (special case)
        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]
        thumb_mcp = landmarks[2]
        
        if is_vertical:
            # Vertical hand: check if thumb is extended sideways
            if orientation == 'right':
                # Right hand: thumb extends to the left
                fingers_up.append(1 if thumb_tip[1] < thumb_ip[1] else 0)
            else:
                # Left hand: thumb extends to the right
                fingers_up.append(1 if thumb_tip[1] > thumb_ip[1] else 0)
        else:
            # Horizontal hand: check if thumb is above
            fingers_up.append(1 if thumb_tip[2] < thumb_mcp[2] else 0)
        
        # Other four fingers
        for i in range(1, 5):
            tip_idx = self.finger_tips[i]
            pip_idx = self.finger_pips[i]
            
            tip = landmarks[tip_idx]
            pip = landmarks[pip_idx]
            
            if is_vertical:
                # Vertical hand: finger is up if tip is above PIP
                fingers_up.append(1 if tip[2] < pip[2] else 0)
            else:
                # Horizontal hand: check based on orientation
                if orientation == 'right':
                    # Fingers extend to the right
                    fingers_up.append(1 if tip[1] > pip[1] else 0)
                else:
                    # Fingers extend to the left
                    fingers_up.append(1 if tip[1] < pip[1] else 0)
        
        return sum(fingers_up)
    
    def draw_finger_indicators(self, frame, landmarks, count, width, height):
        """
        Draw visual indicators for each finger.
        
        Args:
            frame: Video frame
            landmarks: Hand landmarks
            count: Number of fingers up
            width: Frame width
            height: Frame height
        """
        # Draw circles on fingertips
        colors = [(0, 255, 0), (0, 255, 255), (255, 255, 0), (255, 0, 255), (255, 0, 0)]
        
        for i, tip_idx in enumerate(self.finger_tips):
            x = int(landmarks[tip_idx][1] * width)
            y = int(landmarks[tip_idx][2] * height)
            cv2.circle(frame, (x, y), 10, colors[i], cv2.FILLED)
            cv2.circle(frame, (x, y), 12, (255, 255, 255), 2)


class FingerCountApp:
    """Finger counting application."""
    
    def __init__(self):
        """Initialize the application."""
        self.counter = FingerCounter()
        self.capture = None
        self.width = 0
        self.height = 0
        self.prev_time = 0
        
    def draw_count_display(self, frame, count):
        """
        Draw finger count display.
        
        Args:
            frame: Video frame
            count: Number of fingers up
        """
        # Calculate rectangle coordinates
        start_x = int(self.width * 0.85)
        start_y = int(self.height * 0.85)
        end_x = self.width
        end_y = self.height
        
        # Draw background rectangle
        cv2.rectangle(frame, (start_x, start_y), (end_x, end_y), (50, 50, 50), -1)
        cv2.rectangle(frame, (start_x, start_y), (end_x, end_y), (255, 255, 255), 2)
        
        # Draw count text
        text = f"{count}"
        font = cv2.FONT_HERSHEY_PLAIN
        font_scale = 4
        font_thickness = 3
        text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
        
        text_x = start_x + (end_x - start_x - text_size[0]) // 2
        text_y = start_y + (end_y - start_y + text_size[1]) // 2
        
        cv2.putText(frame, text, (text_x, text_y), font, font_scale, 
                   (0, 255, 0), font_thickness)
    
    def draw_instructions(self, frame):
        """Draw usage instructions."""
        instructions = [
            "Show your hand to the camera",
            "Works in any orientation!",
            "Press 'q' to quit"
        ]
        
        y_offset = 30
        for instruction in instructions:
            cv2.putText(frame, instruction, (10, y_offset), 
                       cv2.FONT_HERSHEY_PLAIN, 1.2, (255, 255, 255), 1)
            y_offset += 25
    
    def run(self):
        """Main application loop."""
        # Initialize camera
        self.capture = cv2.VideoCapture(0)
        if not self.capture.isOpened():
            print("[ERROR] Failed to open camera")
            return
        
        self.width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"[INFO] Camera resolution: {self.width} x {self.height}")
        print("[INFO] Starting Finger Counter...")
        print("[INFO] Show your hand in any orientation")
        
        try:
            while True:
                success, frame = self.capture.read()
                if not success:
                    print("[WARNING] Failed to capture frame")
                    break
                
                # Flip frame for mirror effect
                frame = cv2.flip(frame, 1)
                
                # Detect hand
                self.counter.detector.find_hand(frame, draw=True)
                landmarks = self.counter.detector.find_position(frame)
                
                if len(landmarks) != 0:
                    # Count fingers
                    count = self.counter.count_fingers_robust(landmarks)
                    
                    # Draw visual indicators
                    self.counter.draw_finger_indicators(frame, landmarks, count, 
                                                       self.width, self.height)
                    
                    # Draw count display
                    self.draw_count_display(frame, count)
                else:
                    # Show instructions when no hand detected
                    self.draw_instructions(frame)
                
                # Calculate and display FPS
                current_time = time.time()
                fps = 1 / (current_time - self.prev_time) if self.prev_time > 0 else 0
                self.prev_time = current_time
                
                cv2.putText(frame, f"FPS: {int(fps)}", (self.width - 100, 30), 
                           cv2.FONT_HERSHEY_PLAIN, 1.6, (0, 255, 255), 2)
                
                # Display frame
                cv2.imshow("Robust Finger Counter", frame)
                
                # Handle keyboard input
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        except KeyboardInterrupt:
            print("\n[INFO] Application interrupted by user")
        except Exception as e:
            print(f"[ERROR] Application error: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        if self.capture is not None:
            self.capture.release()
        cv2.destroyAllWindows()
        print("[INFO] Application closed")


def main():
    """Entry point for the application."""
    app = FingerCountApp()
    app.run()


if __name__ == "__main__":
    main()