import logging
import threading
import time
from collections.abc import Generator
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

RESOLUTION = (640, 480)
FRAMERATE = 15

_picam2_class: Any = None
_mjpeg_encoder_class: Any = None
_file_output_class: Any = None

try:
    from picamera2 import Picamera2
    from picamera2.encoders import MJPEGEncoder
    from picamera2.outputs import FileOutput

    _picam2_class = Picamera2
    _mjpeg_encoder_class = MJPEGEncoder
    _file_output_class = FileOutput
except (ImportError, Exception):
    logger.warning("picamera2 not available, using stub camera")

# 1x1 white JPEG placeholder
_PLACEHOLDER = (
    b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
    b"\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t"
    b"\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a"
    b"\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342"
    b"\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00"
    b"\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00"
    b"\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b"
    b"\xff\xda\x00\x08\x01\x01\x00\x00?\x00T\xdb\x9e\xa7(\xa0\x00\x00"
    b"\xff\xd9"
)


class _StreamingOutput:
    """MJPEG streaming buffer used by picamera2."""

    def __init__(self) -> None:
        self.frame: bytes | None = None
        self.condition = threading.Condition()

    def write(self, buf: bytes) -> int:
        with self.condition:
            self.frame = buf
            self.condition.notify_all()
        return len(buf)


class Camera:
    def __init__(self) -> None:
        if _picam2_class:
            self._picam2: Any = _picam2_class()
            config = self._picam2.create_video_configuration(
                main={"size": RESOLUTION},
                controls={"FrameRate": FRAMERATE},
            )
            self._picam2.configure(config)
            self._output: _StreamingOutput | None = _StreamingOutput()
            self._encoder: Any = _mjpeg_encoder_class()
        else:
            self._picam2 = None
            self._output = None
            self._encoder = None

    def start(self) -> None:
        if self._picam2:
            self._picam2.start_recording(
                self._encoder,
                _file_output_class(self._output),
            )
            logger.info("Camera started: %s @ %d fps", RESOLUTION, FRAMERATE)
        else:
            logger.info("Stub camera started")

    def stop(self) -> None:
        if self._picam2:
            self._picam2.stop_recording()
            logger.info("Camera stopped")
        else:
            logger.info("Stub camera stopped")

    def stream_frames(self) -> Generator[bytes, None, None]:
        if self._output:
            while True:
                with self._output.condition:
                    self._output.condition.wait()
                    frame = self._output.frame
                if frame:
                    yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")
        else:
            while True:
                yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + _PLACEHOLDER + b"\r\n")
                time.sleep(1.0 / FRAMERATE)

    def save_snapshot(self, path: str) -> None:
        if self._output:
            with self._output.condition:
                self._output.condition.wait()
                frame = self._output.frame
            if frame:
                Path(path).write_bytes(frame)
                logger.info("Snapshot saved: %s", path)
        else:
            Path(path).write_bytes(_PLACEHOLDER)
