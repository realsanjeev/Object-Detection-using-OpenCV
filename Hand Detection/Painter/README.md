# Air Painter - Hand Gesture Drawing Application

A real-time drawing application that uses hand gestures detected via webcam to create digital art.

## Features

- **Gesture-Based Drawing**: Draw using your index finger
- **Color Selection**: Choose from multiple colors (Green, Red, Blue)
- **Eraser Tool**: Remove parts of your drawing
- **Clear Canvas**: Start fresh with one gesture
- **Custom Fonts**: Beautiful UI with custom Iosevka fonts
- **Adjustable Brush**: Change brush thickness on the fly
- **Real-time FPS**: Monitor performance
- **Help System**: Built-in instructions

## Hand Gestures

| Gesture | Action |
|---------|--------|
| Index finger up | **DRAWING** mode - Draw on canvas |
| 2+ fingers up | **SELECTION** mode - Choose colors/tools |
| Other positions | **IDLE** mode - No action |

## Menu Options

The top menu bar contains:
1. **Help** - Display instructions
2. **Green** - Select green color
3. **Red** - Select red color
4. **Blue** - Select blue color
5. **Eraser** - Erase parts of drawing (black color)

## Keyboard Controls

- `q` - Quit application
- `+` or `=` - Increase brush thickness
- `-` or `_` - Decrease brush thickness
- `c` - Clear canvas

## Requirements

```bash
pip install opencv-python mediapipe numpy pillow
```

## File Structure

```
Painter/
├── painter.py              # Main application
├── hand_detector.py        # Hand detection module
├── menu_generator.py       # Menu image generator
├── menu_analysis.py        # Menu analysis tool
├── menu.png               # Menu image
└── assets/
    └── fonts/
        ├── iosevka-bold.ttf
        ├── iosevka-regular.ttf
        └── LICENSE.iosevka.md
```

## Usage

### Run the Painter

```bash
cd "Hand Detection/Painter"
python painter.py
```

### Generate Menu Image

```bash
python menu_generator.py
```

## How It Works

1. **Hand Detection**: Uses MediaPipe to detect hand landmarks in real-time
2. **Gesture Recognition**: Analyzes finger positions to determine mode
3. **Drawing**: Tracks index finger tip position to draw lines
4. **Selection**: Detects finger position over menu regions
5. **Rendering**: Overlays drawing on video feed with custom UI

## Architecture

The application uses an object-oriented design with the `PainterApp` class:

- **Initialization**: Loads fonts, menu, camera, and hand detector
- **Main Loop**: Captures frames, detects hands, processes gestures
- **Mode Handling**: Switches between DRAWING, SELECTION, and IDLE
- **UI Rendering**: Displays FPS, mode, color, and brush size
- **Error Handling**: Robust error handling throughout

## Customization

### Change Colors

Edit the `COLORS` dictionary in `painter.py`:

```python
COLORS = {
    'green': (0, 255, 0),
    'red': (0, 0, 255),
    # Add more colors...
}
```

### Adjust Detection Sensitivity

Modify detector parameters:

```python
self.detector = HandDetector(
    detect_confidence=0.75,  # Detection confidence
    track_confidence=0.5      # Tracking confidence
)
```

### Change Brush Settings

```python
self.brush_thickness = 4  # Default thickness
```

## Troubleshooting

**Camera not opening:**
- Check if camera is being used by another application
- Try changing camera index in `cv2.VideoCapture(0)` to `1` or `2`

**Fonts not loading:**
- Ensure `assets/fonts/` directory exists
- Check font file permissions
- Application will fall back to default fonts

**Hand not detected:**
- Ensure good lighting
- Keep hand within camera frame
- Adjust `detect_confidence` parameter

**Performance issues:**
- Lower camera resolution
- Reduce brush thickness
- Close other applications

## License

This project uses the Iosevka font, which is licensed under the SIL Open Font License 1.1.
See `assets/fonts/LICENSE.iosevka.md` for details.
