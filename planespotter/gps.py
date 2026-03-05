"""GPS coordinate reading. Reads once on startup, saves to config file."""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

CONFIG_PATH = Path(__file__).parent.parent / "config.json"

# Default: observer location from plan
DEFAULT_LAT = 52.403845
DEFAULT_LON = 16.863415


def read_gps() -> tuple[float, float]:
    """Try to read GPS coordinates, fall back to saved config or defaults."""
    # Try live GPS
    try:
        from gps3 import agps3
        gps_socket = agps3.GPSDSocket()
        data_stream = agps3.DataStream()
        gps_socket.connect()
        gps_socket.watch()

        for new_data in gps_socket:
            if new_data:
                data_stream.unpack(new_data)
                lat = data_stream.lat
                lon = data_stream.lon
                if lat != "n/a" and lon != "n/a":
                    lat, lon = float(lat), float(lon)
                    save_config(lat, lon)
                    logger.info("GPS fix: %.6f, %.6f", lat, lon)
                    return lat, lon
    except Exception as e:
        logger.warning("GPS not available: %s", e)

    # Fall back to saved config
    if CONFIG_PATH.exists():
        try:
            cfg = json.loads(CONFIG_PATH.read_text())
            lat, lon = cfg["lat"], cfg["lon"]
            logger.info("Using saved coordinates: %.6f, %.6f", lat, lon)
            return lat, lon
        except (KeyError, json.JSONDecodeError) as e:
            logger.warning("Config file invalid: %s", e)

    # Fall back to defaults
    logger.info("Using default coordinates: %.6f, %.6f", DEFAULT_LAT, DEFAULT_LON)
    save_config(DEFAULT_LAT, DEFAULT_LON)
    return DEFAULT_LAT, DEFAULT_LON


def save_config(lat: float, lon: float) -> None:
    CONFIG_PATH.write_text(json.dumps({"lat": lat, "lon": lon}, indent=2))