"""
Cross-platform Hand Gesture Volume Controller
Supports both Windows (pycaw) and Linux (amixer)
"""
import cv2
import time
import math
import platform
import subprocess
import numpy as np
from hand_detector import HandDetector


class VolumeController:
    """Cross-platform volume controller using hand gestures."""
    
    # Constants for hand landmarks
    THUMB_TIP = 4
    INDEX_FINGER_TIP = 8
    
    # Distance range for volume control
    MIN_VOL_DISTANCE = 19
    MAX_VOL_DISTANCE = 122
    
    def __init__(self):
        """Initialize the volume controller."""
        self.platform = platform.system()
        self.volume_interface = None
        self.min_volume = 0
        self.max_volume = 100
        
        # Initialize platform-specific volume control
        self._initialize_volume_control()
        
    def _initialize_volume_control(self):
        """Initialize volume control based on platform."""
        if self.platform == "Windows":
            self._initialize_windows()
        elif self.platform == "Linux":
            self._initialize_linux()
        elif self.platform == "Darwin":  # macOS
            self._initialize_macos()
        else:
            print(f"[WARNING] Platform '{self.platform}' not fully supported")
            print("[INFO] Volume display will work, but volume control may not")
    
    def _initialize_windows(self):
        """Initialize Windows volume control using pycaw."""
        try:
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self.volume_interface = interface.QueryInterface(IAudioEndpointVolume)
            
            vol_range = self.volume_interface.GetVolumeRange()
            self.min_volume = vol_range[0]
            self.max_volume = vol_range[1]
            
            print(f"[INFO] Windows volume control initialized")
            print(f"[INFO] Volume range: {vol_range}")
        except ImportError:
            print("[ERROR] pycaw not installed. Install with: pip install pycaw comtypes")
            self.volume_interface = None
        except Exception as e:
            print(f"[ERROR] Failed to initialize Windows volume control: {e}")
            self.volume_interface = None
    
    def _initialize_linux(self):
        """Initialize Linux volume control using amixer."""
        try:
            # Test if amixer is available
            result = subprocess.run(['which', 'amixer'], 
                                   capture_output=True, 
                                   text=True)
            if result.returncode == 0:
                print("[INFO] Linux volume control initialized (amixer)")
                self.volume_interface = "amixer"
            else:
                print("[ERROR] amixer not found. Install with: sudo apt install alsa-utils")
                self.volume_interface = None
        except Exception as e:
            print(f"[ERROR] Failed to initialize Linux volume control: {e}")
            self.volume_interface = None
    
    def _initialize_macos(self):
        """Initialize macOS volume control using osascript."""
        try:
            # Test if osascript is available
            result = subprocess.run(['which', 'osascript'], 
                                   capture_output=True, 
                                   text=True)
            if result.returncode == 0:
                print("[INFO] macOS volume control initialized (osascript)")
                self.volume_interface = "osascript"
            else:
                print("[ERROR] osascript not found")
                self.volume_interface = None
        except Exception as e:
            print(f"[ERROR] Failed to initialize macOS volume control: {e}")
            self.volume_interface = None
    
    def set_volume(self, volume_percent):
        """
        Set system volume.
        
        Args:
            volume_percent: Volume level (0-100)
        """
        if self.volume_interface is None:
            return
        
        try:
            if self.platform == "Windows":
                # Map percentage to Windows volume range
                vol_level = np.interp(volume_percent, [0, 100], 
                                     [self.min_volume, self.max_volume])
                self.volume_interface.SetMasterVolumeLevel(vol_level, None)
                
            elif self.platform == "Linux":
                # Use amixer to set volume
                subprocess.run(['amixer', '-D', 'pulse', 'sset', 'Master', 
                              f'{int(volume_percent)}%'], 
                             capture_output=True)
                
            elif self.platform == "Darwin":  # macOS
                # Use osascript to set volume
                subprocess.run(['osascript', '-e', 
                              f'set volume output volume {int(volume_percent)}'],
                             capture_output=True)
        except Exception as e:
            print(f"[ERROR] Failed to set volume: {e}")
    
    def get_volume(self):
        """
        Get current system volume.
        
        Returns:
            float: Current volume percentage (0-100)
        """
        try:
            if self.platform == "Windows" and self.volume_interface:
                vol_level = self.volume_interface.GetMasterVolumeLevel()
                return np.interp(vol_level, [self.min_volume, self.max_volume], [0, 100])
                
            elif self.platform == "Linux":
                result = subprocess.run(['amixer', '-D', 'pulse', 'sget', 'Master'],
                                      capture_output=True, text=True)
                # Parse output to get volume percentage
                import re
                match = re.search(r'\[(\d+)%\]', result.stdout)
                if match:
                    return float(match.group(1))
                    
            elif self.platform == "Darwin":
                result = subprocess.run(['osascript', '-e', 'output volume of (get volume settings)'],
                                      capture_output=True, text=True)
                return float(result.stdout.strip())
        except Exception as e:
            print(f"[ERROR] Failed to get volume: {e}")
        
        return 50  # Default fallback


class VolumeControlApp:
    """Hand gesture volume control application."""
    
    def __init__(self):
        """Initialize the application."""
        self.controller = VolumeController()
        self.detector = None
        self.capture = None
        self.prev_time = 0
        
    def draw_ui(self, frame, x1, y1, x2, y2, volume_percent, fps):
        """
        Draw UI elements on frame.
        
        Args:
            frame: Video frame
            x1, y1: Thumb tip coordinates
            x2, y2: Index finger tip coordinates
            volume_percent: Current volume percentage
            fps: Current FPS
        """
        # Draw line between fingers
        cv2.line(frame, (x1, y1), (x2, y2), (255, 255, 0), 3)
        
        # Draw circles at fingertips
        cv2.circle(frame, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
        cv2.circle(frame, (x2, y2), 10, (255, 0, 255), cv2.FILLED)
        
        # Display volume percentage
        cv2.putText(frame, f"VOL: {int(volume_percent)}%", (10, 90), 
                   cv2.FONT_HERSHEY_PLAIN, 1.3, (155, 155, 255), 3)
        
        # Draw volume bar
        cv2.rectangle(frame, (10, 100), (40, 300), (0, 0, 255), 1)
        y_vol = int(np.interp(volume_percent, [0, 100], [300, 100]))
        cv2.rectangle(frame, (10, y_vol), (40, 300), (0, 255, 0), cv2.FILLED)
        
        # Display FPS
        cv2.putText(frame, f"FPS: {int(fps)}", (10, 40),
                   cv2.FONT_HERSHEY_PLAIN, 1.2, (0, 255, 255), 1)
        
        # Display platform info
        platform_text = f"Platform: {self.controller.platform}"
        cv2.putText(frame, platform_text, (10, 70),
                   cv2.FONT_HERSHEY_PLAIN, 1.0, (200, 200, 200), 1)
    
    def run(self):
        """Main application loop."""
        # Initialize camera
        self.capture = cv2.VideoCapture(0)
        if not self.capture.isOpened():
            print("[ERROR] Failed to open camera")
            return
        
        # Initialize hand detector
        self.detector = HandDetector(detect_confidence=0.7, track_confidence=0.5)
        
        print("[INFO] Starting Volume Controller...")
        print("[INFO] Press 'q' to quit")
        print("[INFO] Pinch thumb and index finger to control volume")
        
        try:
            while True:
                success, frame = self.capture.read()
                if not success:
                    print("[WARNING] Failed to capture frame")
                    break
                
                # Flip frame for mirror effect
                frame = cv2.flip(frame, 1)
                
                # Detect hand
                self.detector.find_hand(frame, draw=False)
                landmarks = self.detector.find_position(frame)
                
                if len(landmarks) != 0:
                    # Get finger positions
                    h, w, c = frame.shape
                    x1 = int(landmarks[self.controller.THUMB_TIP][1] * w)
                    y1 = int(landmarks[self.controller.THUMB_TIP][2] * h)
                    x2 = int(landmarks[self.controller.INDEX_FINGER_TIP][1] * w)
                    y2 = int(landmarks[self.controller.INDEX_FINGER_TIP][2] * h)
                    
                    # Calculate distance between fingers
                    distance = int(math.hypot(x2 - x1, y2 - y1))
                    
                    # Map distance to volume
                    volume_percent = np.interp(distance, 
                                              [self.controller.MIN_VOL_DISTANCE, 
                                               self.controller.MAX_VOL_DISTANCE], 
                                              [0, 100])
                    
                    # Set system volume
                    self.controller.set_volume(volume_percent)
                    
                    # Calculate FPS
                    current_time = time.time()
                    fps = 1 / (current_time - self.prev_time) if self.prev_time > 0 else 0
                    self.prev_time = current_time
                    
                    # Draw UI
                    self.draw_ui(frame, x1, y1, x2, y2, volume_percent, fps)
                
                # Display frame
                cv2.imshow("Hand Gesture Volume Control", frame)
                
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
    app = VolumeControlApp()
    app.run()


if __name__ == "__main__":
    main()
