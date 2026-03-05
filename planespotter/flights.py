import asyncio
import logging
from dataclasses import dataclass

import httpx

logger = logging.getLogger(__name__)

OPENSKY_URL = "https://opensky-network.org/api/states/all"

BBOX = {
    "lamin": 52.35,
    "lamax": 52.50,
    "lomin": 16.75,
    "lomax": 16.95,
}

POLL_INTERVAL = 15  # in seconds


@dataclass
class Aircraft:
    icao24: str
    callsign: str | None
    origin_country: str
    longitude: float | None
    latitude: float | None
    baro_altitude: float | None
    on_ground: bool
    velocity: float | None
    true_track: float | None
    vertical_rate: float | None
    geo_altitude: float | None
    squawk: str | None

    @classmethod
    def from_state_vector(cls, sv: list) -> "Aircraft":
        return cls(
            icao24=sv[0],
            callsign=sv[1].strip() if sv[1] else None,
            origin_country=sv[2],
            longitude=sv[5],
            latitude=sv[6],
            baro_altitude=sv[7],
            on_ground=sv[8],
            velocity=sv[9],
            true_track=sv[10],
            vertical_rate=sv[11],
            geo_altitude=sv[13],
            squawk=sv[14],
        )

    def to_dict(self) -> dict:
        return {
            "icao24": self.icao24,
            "callsign": self.callsign,
            "origin_country": self.origin_country,
            "longitude": self.longitude,
            "latitude": self.latitude,
            "baro_altitude": self.baro_altitude,
            "on_ground": self.on_ground,
            "velocity": self.velocity,
            "true_track": self.true_track,
            "vertical_rate": self.vertical_rate,
            "geo_altitude": self.geo_altitude,
            "squawk": self.squawk,
        }


class FlightTracker:
    def __init__(self) -> None:
        self.aircraft: list[Aircraft] = []
        self._running = False

    async def fetch_once(self) -> list[Aircraft]:
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                resp = await client.get(OPENSKY_URL, params=BBOX)
                resp.raise_for_status()
                data = resp.json()
            except (httpx.HTTPError, Exception) as e:
                logger.error("OpenSky API error: %s", e)
                return self.aircraft  # return cached data on error

        states = data.get("states") or []
        self.aircraft = [
            Aircraft.from_state_vector(sv)
            for sv in states
            if sv[5] is not None and sv[6] is not None  # skip if no position
        ]
        logger.info("Fetched %d aircraft", len(self.aircraft))
        return self.aircraft

    async def poll(self) -> None:
        self._running = True
        while self._running:
            await self.fetch_once()
            await asyncio.sleep(POLL_INTERVAL)

    def stop(self) -> None:
        self._running = False
