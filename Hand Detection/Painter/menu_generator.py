"""
Menu generator for the Air Painter application.
Creates a visual menu bar with color options and controls.
"""
import cv2
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def create_menu(width=640, height=80):
    """
    Create a menu bar with painting options.
    
    Args:
        width: Width of the menu
        height: Height of the menu
        
    Returns:
        numpy array: Menu image in BGR format
    """
    # Create blank menu
    menu = np.ones((height, width, 3), dtype=np.uint8) * 50  # Dark gray background
    
    # Define menu sections
    sections = [
        {'name': 'Help', 'color': (100, 100, 100), 'x': 0},
        {'name': 'Green', 'color': (0, 255, 0), 'x': 128},
        {'name': 'Red', 'color': (0, 0, 255), 'x': 256},
        {'name': 'Blue', 'color': (255, 0, 0), 'x': 384},
        {'name': 'Eraser', 'color': (0, 0, 0), 'x': 512},
        {'name': 'Clear', 'color': (200, 200, 200), 'x': 640}
    ]
    
    section_width = 128
    
    # Draw sections
    for i, section in enumerate(sections):
        x_start = section['x']
        x_end = x_start + section_width if i < len(sections) - 1 else width
        
        # Draw color box
        color_box_y = 15
        color_box_height = 30
        cv2.rectangle(menu, 
                     (x_start + 10, color_box_y), 
                     (x_end - 10, color_box_y + color_box_height), 
                     section['color'], -1)
        cv2.rectangle(menu, 
                     (x_start + 10, color_box_y), 
                     (x_end - 10, color_box_y + color_box_height), 
                     (255, 255, 255), 1)
        
        # Add text label
        text = section['name']
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        thickness = 1
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        text_x = x_start + (section_width - text_size[0]) // 2
        text_y = color_box_y + color_box_height + 20
        
        cv2.putText(menu, text, (text_x, text_y), font, font_scale, 
                   (255, 255, 255), thickness)
        
        # Draw separator
        if i < len(sections) - 1:
            cv2.line(menu, (x_end, 0), (x_end, height), (100, 100, 100), 1)
    
    return menu


def create_menu_with_custom_font(width=640, height=80):
    """
    Create menu with custom fonts if available.
    
    Args:
        width: Width of the menu
        height: Height of the menu
        
    Returns:
        numpy array: Menu image in BGR format
    """
    try:
        # Try to load custom font
        font_path = Path("assets/fonts/iosevka-bold.ttf")
        if font_path.exists():
            # Create PIL image
            img = Image.new('RGB', (width, height), color=(50, 50, 50))
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype(str(font_path), 16)
            
            sections = [
                {'name': 'Help', 'color': (100, 100, 100), 'x': 0},
                {'name': 'Green', 'color': (0, 255, 0), 'x': 128},
                {'name': 'Red', 'color': (0, 0, 255), 'x': 256},
                {'name': 'Blue', 'color': (255, 0, 0), 'x': 384},
                {'name': 'Eraser', 'color': (0, 0, 0), 'x': 512},
            ]
            
            section_width = 128
            
            for i, section in enumerate(sections):
                x_start = section['x']
                x_end = min(x_start + section_width, width)
                
                # Draw color box
                color = section['color'][::-1]  # BGR to RGB
                draw.rectangle([(x_start + 10, 15), (x_end - 10, 45)], 
                             fill=color, outline=(255, 255, 255))
                
                # Add text
                text = section['name']
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_x = x_start + (section_width - text_width) // 2
                draw.text((text_x, 55), text, font=font, fill=(255, 255, 255))
                
                # Draw separator
                if i < len(sections) - 1:
                    draw.line([(x_end, 0), (x_end, height)], fill=(100, 100, 100))
            
            # Convert to OpenCV format
            menu = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            return menu
        else:
            return create_menu(width, height)
    except Exception as e:
        print(f"[WARNING] Failed to create menu with custom font: {e}")
        return create_menu(width, height)


def main():
    """Generate and save menu image."""
    print("[INFO] Generating menu image...")
    
    # Create menu
    menu = create_menu_with_custom_font()
    
    # Save menu
    output_path = "menu.png"
    cv2.imwrite(output_path, menu)
    print(f"[INFO] Menu saved to: {output_path}")
    
    # Display menu
    cv2.imshow("Menu Preview", menu)
    print("[INFO] Press any key to close...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
