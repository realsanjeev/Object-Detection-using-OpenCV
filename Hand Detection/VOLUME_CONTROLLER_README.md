# Cross-Platform Hand Gesture Volume Controller

A unified volume controller that works across Windows, Linux, and macOS using hand gestures detected via webcam.

## Features

- **Cross-Platform Support**: Automatically detects and adapts to Windows, Linux, or macOS
- **Hand Gesture Control**: Pinch thumb and index finger to adjust volume
- **Real-time Feedback**: Visual volume bar and percentage display
- **FPS Monitoring**: Performance tracking
- **Robust Error Handling**: Graceful fallbacks if platform-specific libraries unavailable
- **OOP Design**: Clean, maintainable code structure

## Platform-Specific Requirements

### Windows
```bash
pip install pycaw comtypes
```

### Linux
```bash
sudo apt install alsa-utils
```

### macOS
No additional installation required (uses built-in `osascript`)

## Common Requirements

```bash
pip install opencv-python mediapipe numpy
```

## Usage

```bash
cd "Hand Detection"
python volume_controller.py
```

## How It Works

1. **Platform Detection**: Automatically detects your operating system
2. **Volume Interface**: Initializes appropriate volume control method:
   - Windows: pycaw library
   - Linux: amixer command
   - macOS: osascript command
3. **Hand Detection**: Uses MediaPipe to detect hand landmarks
4. **Gesture Recognition**: Measures distance between thumb and index finger
5. **Volume Mapping**: Maps finger distance to volume level (0-100%)
6. **System Control**: Adjusts system volume in real-time

## Controls

- **Pinch fingers**: Bring thumb and index finger closer to decrease volume
- **Spread fingers**: Move thumb and index finger apart to increase volume
- **Press 'q'**: Quit application

## Architecture

### VolumeController Class
- Handles platform-specific volume control
- Provides unified interface for getting/setting volume
- Automatic platform detection and initialization

### VolumeControlApp Class
- Manages camera and hand detection
- Processes gestures and updates volume
- Renders UI elements

## Troubleshooting

**Windows: pycaw not working**
- Install Visual C++ Redistributable
- Run: `pip install --upgrade pycaw comtypes`

**Linux: amixer not found**
- Install: `sudo apt install alsa-utils`
- Check audio device: `amixer -D pulse sget Master`

**macOS: Permission denied**
- Grant camera permissions in System Preferences
- Ensure Terminal/IDE has accessibility permissions

**Camera not opening**
- Check if camera is in use by another application
- Try changing camera index: `cv2.VideoCapture(1)` or `(2)`

**Hand not detected**
- Ensure good lighting conditions
- Keep hand within camera frame
- Adjust detection confidence in code

## Migration from Old Files

This unified file replaces:
- `volume_controller.py` (Windows-only)
- `volume_controller_linux.py` (Linux-only)

The old files have been kept for reference but are no longer needed.

## License

Part of the Object Detection using OpenCV project.
