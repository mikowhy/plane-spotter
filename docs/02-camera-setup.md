# Step 2 -- Camera Setup

## Hardware

Connect the Camera Rev 1.3 FFC cable to the CSI slot on the Pi. Make sure the blue side faces the Ethernet port.

## Configuration

On Bookworm, the camera is auto-detected. No raspi-config needed.

Verify in `/boot/firmware/config.txt`:

```ini
camera_auto_detect=1
```

> Config files on Bookworm are at `/boot/firmware/`, NOT `/boot/`.

## Test

```bash
sudo reboot

# After reboot:
rpicam-hello --list-cameras    # should detect ov5647
rpicam-still -o test.jpg       # take a test photo
```

If auto-detect fails, manually specify in `/boot/firmware/config.txt`:

```ini
camera_auto_detect=0
dtoverlay=ov5647
```

## Streaming Architecture

For the MJPEG stream, use the hardware encoder pipeline:

1. `Picamera2()` with `create_video_configuration(main={"size": (640, 480)})`
2. `MJPEGEncoder()` -- uses VideoCore GPU, ~50% CPU vs ~95% for software
3. `_StreamingOutput(io.BufferedIOBase)` class with `threading.Condition` for multi-client frame sharing
4. `FileOutput(streaming_output)` wired to encoder
5. `picam2.start_recording(encoder, output)` starts the pipeline
6. FastAPI `StreamingResponse` with async generator yielding MJPEG frames

Content type: `multipart/x-mixed-replace; boundary=frame`