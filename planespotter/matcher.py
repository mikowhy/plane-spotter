"""Determines which aircraft is closest to the observer / on approach."""

import math

from planespotter.flights import Aircraft

# Observer location (Poznan, ~2.9km east of runway 28 threshold)
HOME_LAT = 52.403845
HOME_LON = 16.863415

# Lawica Airport
AIRPORT_LAT = 52.4205
AIRPORT_LON = 16.8310

# Runway 28 approach heading (aircraft flying westbound)
APPROACH_HEADING = 288  # degrees

# Alert radius in km
ALERT_RADIUS_KM = 3.0

EARTH_RADIUS_KM = 6371.0


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distance in km between two points on Earth."""
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return EARTH_RADIUS_KM * 2 * math.asin(math.sqrt(a))


def heading_diff(h1: float, h2: float) -> float:
    """Smallest angle between two headings (0-180)."""
    d = abs(h1 - h2) % 360
    return d if d <= 180 else 360 - d


def is_on_approach(ac: Aircraft) -> bool:
    """Check if aircraft is likely on approach to runway 28."""
    if ac.on_ground or ac.true_track is None or ac.baro_altitude is None:
        return False
    # Below 1500m and heading roughly matches approach
    if ac.baro_altitude > 1500:
        return False
    if (
        heading_diff(
            h1=ac.true_track,
            h2=APPROACH_HEADING,
        )
        > 30
    ):
        return False
    return True


def distance_to_home(ac: Aircraft) -> float | None:
    """Distance in km from aircraft to observer. None if no position."""
    if ac.latitude is None or ac.longitude is None:
        return None
    return haversine(
        lat1=HOME_LAT,
        lon1=HOME_LON,
        lat2=ac.latitude,
        lon2=ac.longitude,
    )


def find_closest(aircraft: list[Aircraft]) -> Aircraft | None:
    """Find the aircraft closest to the observer."""
    closest = None
    min_dist = float("inf")
    for ac in aircraft:
        dist = distance_to_home(ac)
        if dist is not None and dist < min_dist:
            min_dist = dist
            closest = ac
    return closest


def find_approaching(aircraft: list[Aircraft]) -> list[Aircraft]:
    """Find aircraft on approach to runway 28, sorted by distance to home."""
    approaching = [ac for ac in aircraft if is_on_approach(ac)]
    approaching.sort(key=lambda ac: distance_to_home(ac) or float("inf"))
    return approaching


def get_nearby(aircraft: list[Aircraft], radius_km: float = ALERT_RADIUS_KM) -> list[Aircraft]:
    """Aircraft within alert radius of observer."""
    return [ac for ac in aircraft if (d := distance_to_home(ac)) is not None and d <= radius_km]
