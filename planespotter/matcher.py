"""Determines which aircraft is closest to the observer / on approach."""

import math

from planespotter.flights import Aircraft

HOME_LAT = 52.403845
HOME_LON = 16.863415


def set_home(lat: float, lon: float) -> None:
    global HOME_LAT, HOME_LON
    HOME_LAT = lat
    HOME_LON = lon


# Lawica Airport
AIRPORT_LAT = 52.4205
AIRPORT_LON = 16.8310

# Runway 28 approach heading (aircraft flying westbound)
APPROACH_HEADING = 288  # degrees

# Alert radius in km
ALERT_RADIUS_KM = 3.0

EARTH_RADIUS_KM = 6371.0


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    haversine_a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return EARTH_RADIUS_KM * 2 * math.asin(math.sqrt(haversine_a))


def heading_diff(heading1: float, heading2: float) -> float:
    diff = abs(heading1 - heading2) % 360
    return diff if diff <= 180 else 360 - diff


def is_on_approach(aircraft: Aircraft) -> bool:
    if aircraft.on_ground or aircraft.true_track is None or aircraft.baro_altitude is None:
        return False
    if aircraft.baro_altitude > 1500:
        return False
    if (
        heading_diff(
            heading1=aircraft.true_track,
            heading2=APPROACH_HEADING,
        )
        > 30
    ):
        return False
    return True


def distance_to_home(aircraft: Aircraft) -> float | None:
    if aircraft.latitude is None or aircraft.longitude is None:
        return None
    return haversine(
        lat1=HOME_LAT,
        lon1=HOME_LON,
        lat2=aircraft.latitude,
        lon2=aircraft.longitude,
    )


def find_closest(aircraft: list[Aircraft]) -> Aircraft | None:
    closest = None
    min_dist = float("inf")
    for plane in aircraft:
        dist = distance_to_home(plane)
        if dist is not None and dist < min_dist:
            min_dist = dist
            closest = plane
    return closest


def find_approaching(aircraft: list[Aircraft]) -> list[Aircraft]:
    approaching = [plane for plane in aircraft if is_on_approach(plane)]
    approaching.sort(key=lambda plane: distance_to_home(plane) or float("inf"))
    return approaching


def get_nearby(aircraft: list[Aircraft], radius_km: float = ALERT_RADIUS_KM) -> list[Aircraft]:
    return [plane for plane in aircraft if (dist := distance_to_home(plane)) is not None and dist <= radius_km]
