import cv2
import time
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from hand_detector import HandDetector


class PainterApp:
    """Air Painter application using hand gestures for drawing."""
    
    # Color palette (BGR format)
    COLORS = {
        'green': (0, 255, 0),
        'red': (0, 0, 255),
        'blue': (255, 0, 0),
        'black': (0, 0, 0),
        'white': (255, 255, 255),
        'yellow': (0, 255, 255),
        'cyan': (255, 255, 0),
        'magenta': (255, 0, 255)
    }
    
    # Menu regions (x_min, x_max, y_max)
    MENU_REGIONS = {
        'help': (0, 128, 80),
        'green': (128, 256, 80),
        'red': (256, 384, 80),
        'blue': (384, 512, 80),
        'eraser': (512, 640, 80)
    }
    
    def __init__(self):
        """Initialize the Painter application."""
        self.menu = None
        self.capture = None
        self.width = 0
        self.height = 0
        self.draw_canvas = None
        self.detector = None
        self.prev_time = 0
        self.xp, self.yp = None, None
        self.current_color = self.COLORS['green']
        self.brush_thickness = 4
        self.font_regular = None
        self.font_bold = None
        
    def load_fonts(self):
        """Load custom fonts from assets directory."""
        try:
            font_dir = Path("assets/fonts")
            regular_font = font_dir / "iosevka-regular.ttf"
            bold_font = font_dir / "iosevka-bold.ttf"
            
            if regular_font.exists():
                self.font_regular = ImageFont.truetype(str(regular_font), 20)
                print(f"[INFO] Loaded regular font: {regular_font}")
            else:
                print(f"[WARNING] Regular font not found, using default")
                self.font_regular = ImageFont.load_default()
                
            if bold_font.exists():
                self.font_bold = ImageFont.truetype(str(bold_font), 24)
                print(f"[INFO] Loaded bold font: {bold_font}")
            else:
                print(f"[WARNING] Bold font not found, using default")
                self.font_bold = ImageFont.load_default()
                
        except Exception as e:
            print(f"[ERROR] Failed to load fonts: {e}")
            self.font_regular = ImageFont.load_default()
            self.font_bold = ImageFont.load_default()
    
    def put_text_pil(self, img, text, position, font, color=(255, 255, 255)):
        """Put text on image using PIL for better font rendering."""
        # Convert BGR to RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img_rgb)
        draw = ImageDraw.Draw(pil_img)
        
        # Draw text
        draw.text(position, text, font=font, fill=color[::-1])  # Reverse BGR to RGB
        
        # Convert back to BGR
        img_bgr = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        img[:] = img_bgr
        
    def initialize(self):
        """Initialize all components."""
        # Load fonts
        self.load_fonts()
        
        # Load menu image
        self.menu = cv2.imread("menu.png")
        if self.menu is None:
            print("[ERROR] Failed to load menu.png")
            return False
        
        # Set up video capture
        self.capture = cv2.VideoCapture(0)
        if not self.capture.isOpened():
            print("[ERROR] Failed to open camera")
            return False
            
        self.width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.draw_canvas = np.zeros((self.height, self.width, 3), dtype="uint8")
        
        print(f"[INFO] Video resolution: {self.width} x {self.height}")
        
        # Resize menu image
        self.menu = cv2.resize(self.menu, (self.width, self.menu.shape[0]))
        print(f"[INFO] Menu shape: {self.menu.shape}")
        
        # Initialize hand detector
        self.detector = HandDetector(detect_confidence=0.75, track_confidence=0.5)
        
        return True
    
    def get_mode_from_fingers(self, up_fingers):
        """Determine mode based on finger configuration."""
        count = up_fingers.count(1)
        
        # Index finger only = Drawing
        if count == 1 and up_fingers[1] == 1:
            return "DRAWING"
        # Two or more fingers = Selection
        elif count >= 2:
            return "SELECTION"
        # Otherwise = Idle
        else:
            return "IDLE"
    
    def handle_selection(self, x, y, frame):
        """Handle selection mode interactions."""
        # Reset drawing position
        self.xp, self.yp = None, None
        
        # Check which region was selected
        for region_name, (x_min, x_max, y_max) in self.MENU_REGIONS.items():
            if x_min <= x <= x_max and y <= y_max:
                if region_name == 'help':
                    self.show_help(frame)
                elif region_name == 'green':
                    self.current_color = self.COLORS['green']
                elif region_name == 'red':
                    self.current_color = self.COLORS['red']
                elif region_name == 'blue':
                    self.current_color = self.COLORS['blue']
                elif region_name == 'eraser':
                    self.current_color = self.COLORS['black']
                break
    
    def show_help(self, frame):
        """Display help instructions on frame."""
        instructions = [
            "PAINTER INSTRUCTIONS:",
            "1 finger (index): DRAWING mode",
            "2+ fingers: SELECTION mode",
            "Other: IDLE mode",
            "",
            "Menu: Help | Green | Red | Blue | Eraser",
            "Keys: +/- (brush) | c (clear) | q (quit)"
        ]
        
        # Calculate help box dimensions
        menu_height = self.menu.shape[0]
        line_height = 30
        padding = 15
        box_width = 450
        box_height = len(instructions) * line_height + 2 * padding
        
        # Position in center-left, below menu
        box_x = 150
        box_y = menu_height + 50
        
        # Draw semi-transparent background
        overlay = frame.copy()
        cv2.rectangle(overlay, (box_x - padding, box_y - padding), 
                     (box_x + box_width, box_y + box_height), 
                     (40, 40, 40), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Draw border
        cv2.rectangle(frame, (box_x - padding, box_y - padding), 
                     (box_x + box_width, box_y + box_height), 
                     (255, 255, 255), 2)
        
        # Draw text
        y_offset = box_y
        for line in instructions:
            self.put_text_pil(frame, line, (box_x, y_offset), self.font_regular, (255, 255, 255))
            y_offset += line_height
    
    def handle_drawing(self, x, y):
        """Handle drawing mode."""
        if self.xp is None or self.yp is None:
            self.xp, self.yp = x, y
        else:
            cv2.line(self.draw_canvas, (self.xp, self.yp), (x, y), 
                    self.current_color, thickness=self.brush_thickness)
            self.xp, self.yp = x, y
    
    def clear_canvas(self):
        """Clear the drawing canvas."""
        self.draw_canvas = np.zeros((self.height, self.width, 3), dtype="uint8")
        print("[INFO] Canvas cleared")
    
    def draw_ui(self, frame, fps, mode):
        """Draw UI elements on frame."""
        menu_height = self.menu.shape[0]  # Get menu height (80px)
        
        # FPS counter - bottom left
        fps_text = f"FPS: {int(fps)}"
        self.put_text_pil(frame, fps_text, (10, self.height - 40), 
                         self.font_regular, (155, 89, 255))
        
        # Current color indicator - below menu on left
        color_y = menu_height + 10
        self.put_text_pil(frame, "Color:", (10, color_y), self.font_bold, (255, 255, 255))
        cv2.rectangle(frame, (80, color_y + 5), (110, color_y + 25), self.current_color, -1)
        cv2.rectangle(frame, (80, color_y + 5), (110, color_y + 25), (255, 255, 255), 1)
        
        # Mode indicator - below menu on right
        mode_text = f"Mode: {mode}"
        self.put_text_pil(frame, mode_text, (self.width - 200, menu_height + 10), 
                         self.font_regular, (0, 255, 255))
        
        # Brush thickness indicator - below mode on right
        thickness_text = f"Brush: {self.brush_thickness}px"
        self.put_text_pil(frame, thickness_text, (self.width - 200, menu_height + 40), 
                         self.font_regular, (255, 255, 255))
    
    def run(self):
        """Main application loop."""
        if not self.initialize():
            return
        
        print("[INFO] Starting Painter application...")
        print("[INFO] Press 'q' to quit, '+'/'-' to adjust brush size")
        
        try:
            while True:
                # Capture frame
                success, frame = self.capture.read()
                if not success:
                    print("[WARNING] Failed to capture frame")
                    break
                
                # Flip frame for mirror effect
                frame = cv2.flip(frame, 1)
                
                # Detect hand
                self.detector.find_hand(frame, draw=False)
                landmarks = self.detector.find_position(frame)
                
                mode = "IDLE"
                
                if len(landmarks) != 0:
                    # Get index finger tip position
                    x1 = int(landmarks[8][1] * self.width)
                    y1 = int(landmarks[8][2] * self.height)
                    
                    # Get finger status
                    up_fingers = self.detector.fingerUp(landmarks)
                    mode = self.get_mode_from_fingers(up_fingers)
                    
                    # Draw cursor
                    if mode != "IDLE":
                        cv2.circle(frame, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
                    
                    # Handle modes
                    if mode == "SELECTION":
                        self.handle_selection(x1, y1, frame)
                    elif mode == "DRAWING":
                        self.handle_drawing(x1, y1)
                    else:
                        self.xp, self.yp = None, None
                else:
                    self.xp, self.yp = None, None
                
                # Merge drawing canvas with frame
                gray = cv2.cvtColor(self.draw_canvas, cv2.COLOR_BGR2GRAY)
                _, inv_mask = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
                inv_mask = cv2.cvtColor(inv_mask, cv2.COLOR_GRAY2BGR)
                
                frame = cv2.bitwise_and(frame, cv2.bitwise_not(inv_mask))
                frame = cv2.bitwise_or(frame, self.draw_canvas)
                
                # Overlay menu
                frame[0:self.menu.shape[0], 0:self.width] = self.menu
                
                # Calculate FPS
                current_time = time.time()
                fps = 1 / (current_time - self.prev_time) if self.prev_time > 0 else 0
                self.prev_time = current_time
                
                # Draw UI
                self.draw_ui(frame, fps, mode)
                
                # Display frame
                cv2.imshow("Air Painter", frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('+') or key == ord('='):
                    self.brush_thickness = min(20, self.brush_thickness + 1)
                elif key == ord('-') or key == ord('_'):
                    self.brush_thickness = max(1, self.brush_thickness - 1)
                elif key == ord('c'):
                    self.clear_canvas()
                    
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
    app = PainterApp()
    app.run()


if __name__ == "__main__":
    main()
