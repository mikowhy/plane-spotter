"""Entry point -- starts all services with asyncio."""

import asyncio
import logging

import uvicorn

from planespotter.camera import Camera
from planespotter.flights import FlightTracker
from planespotter.gpio import StatusLED
from planespotter.gps import read_gps
from planespotter.database import init_db
from planespotter import api

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def led_heartbeat(led: StatusLED) -> None:
    led.blink(on_time=0.5, off_time=2.0)
    while True:
        await asyncio.sleep(60)


async def main() -> None:
    # Read GPS (once)
    lat, lon = read_gps()
    logger.info("Observer position: %.6f, %.6f", lat, lon)

    # Init database
    await init_db()

    # Start camera
    cam = Camera()
    cam.start()

    # Start flight tracker
    tracker = FlightTracker()

    # Wire up API
    api.setup(cam, tracker)

    # Start LED
    led = StatusLED()

    # Run all tasks
    config = uvicorn.Config(
        api.app, host="0.0.0.0", port=8000, log_level="info"
    )
    server = uvicorn.Server(config)

    try:
        await asyncio.gather(
            server.serve(),
            tracker.poll(),
            led_heartbeat(led),
        )
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        tracker.stop()
        cam.stop()
        led.off()


if __name__ == "__main__":
    asyncio.run(main())