"""Entry point -- starts all services with asyncio."""

import asyncio
import logging

import uvicorn

from planespotter import api
from planespotter.camera import Camera
from planespotter.database import init_db
from planespotter.flights import FlightTracker
from planespotter.gpio import StatusLED
from planespotter.gps import read_gps
from planespotter.matcher import set_home

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def led_heartbeat(led: StatusLED) -> None:
    led.blink(
        on_time=0.5,
        off_time=2.0,
    )
    while True:
        await asyncio.sleep(60)


async def main() -> None:
    lat, lon = read_gps()
    set_home(
        lat=lat,
        lon=lon,
    )
    logger.info("Observer position: %.6f, %.6f", lat, lon)

    await init_db()

    camera = Camera()
    camera.start()
    tracker = FlightTracker()
    api.setup(
        camera_instance=camera,
        tracker_instance=tracker,
    )
    led = StatusLED()
    config = uvicorn.Config(
        app=api.app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
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
        camera.stop()
        led.off()


if __name__ == "__main__":
    asyncio.run(main())
