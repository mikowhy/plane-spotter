"""Tests for the matcher module."""

from typing import Any

from planespotter.flights import Aircraft
from planespotter.matcher import (
    distance_to_home,
    find_approaching,
    find_closest,
    get_nearby,
    haversine,
    heading_diff,
    is_on_approach,
)


def _make_aircraft(**overrides: Any) -> Aircraft:
    defaults = dict(
        icao24="abc123",
        callsign="TEST123",
        origin_country="Poland",
        longitude=16.863,
        latitude=52.404,
        baro_altitude=300.0,
        on_ground=False,
        velocity=70.0,
        true_track=288.0,
        vertical_rate=-3.0,
        geo_altitude=310.0,
        squawk=None,
    )
    defaults.update(overrides)
    return Aircraft(**defaults)


class TestHaversine:
    def test_same_point(self) -> None:
        assert (
            haversine(
                lat1=52.0,
                lon1=16.0,
                lat2=52.0,
                lon2=16.0,
            )
            == 0.0
        )

    def test_known_distance(self) -> None:
        # Home to Lawica airport ~2.9km
        dist = haversine(
            lat1=52.403845,
            lon1=16.863415,
            lat2=52.4205,
            lon2=16.8310,
        )
        assert 2.5 < dist < 3.5

    def test_symmetry(self) -> None:
        dist_forward = haversine(
            lat1=52.0,
            lon1=16.0,
            lat2=53.0,
            lon2=17.0,
        )
        dist_reverse = haversine(
            lat1=53.0,
            lon1=17.0,
            lat2=52.0,
            lon2=16.0,
        )
        assert abs(dist_forward - dist_reverse) < 0.001


class TestHeadingDiff:
    def test_same_heading(self) -> None:
        assert (
            heading_diff(
                heading1=90,
                heading2=90,
            )
            == 0
        )

    def test_opposite(self) -> None:
        assert (
            heading_diff(
                heading1=0,
                heading2=180,
            )
            == 180
        )

    def test_wraparound(self) -> None:
        assert (
            heading_diff(
                heading1=350,
                heading2=10,
            )
            == 20
        )

    def test_wraparound_reverse(self) -> None:
        assert (
            heading_diff(
                heading1=10,
                heading2=350,
            )
            == 20
        )


class TestIsOnApproach:
    def test_on_approach(self) -> None:
        plane = _make_aircraft(baro_altitude=300, true_track=285)
        assert is_on_approach(plane) is True

    def test_too_high(self) -> None:
        plane = _make_aircraft(baro_altitude=2000, true_track=288)
        assert is_on_approach(plane) is False

    def test_wrong_heading(self) -> None:
        plane = _make_aircraft(baro_altitude=300, true_track=90)
        assert is_on_approach(plane) is False

    def test_on_ground(self) -> None:
        plane = _make_aircraft(on_ground=True, baro_altitude=0, true_track=288)
        assert is_on_approach(plane) is False

    def test_no_altitude(self) -> None:
        plane = _make_aircraft(baro_altitude=None, true_track=288)
        assert is_on_approach(plane) is False

    def test_no_track(self) -> None:
        plane = _make_aircraft(baro_altitude=300, true_track=None)
        assert is_on_approach(plane) is False


class TestDistanceToHome:
    def test_with_position(self) -> None:
        plane = _make_aircraft(latitude=52.403845, longitude=16.863415)
        dist = distance_to_home(plane)
        assert dist is not None
        assert dist < 0.01  # basically at home

    def test_no_position(self) -> None:
        plane = _make_aircraft(latitude=None, longitude=None)
        assert distance_to_home(plane) is None


class TestFindClosest:
    def test_finds_closest(self) -> None:
        far = _make_aircraft(icao24="far", latitude=52.45, longitude=16.90)
        close = _make_aircraft(icao24="close", latitude=52.404, longitude=16.864)
        result = find_closest([far, close])
        assert result is not None
        assert result.icao24 == "close"

    def test_empty_list(self) -> None:
        assert find_closest([]) is None


class TestFindApproaching:
    def test_sorted_by_distance(self) -> None:
        far = _make_aircraft(
            icao24="far",
            latitude=52.45,
            longitude=16.90,
            baro_altitude=500,
            true_track=288,
        )
        close = _make_aircraft(
            icao24="close",
            latitude=52.404,
            longitude=16.864,
            baro_altitude=300,
            true_track=285,
        )
        result = find_approaching([far, close])
        assert len(result) == 2
        assert result[0].icao24 == "close"

    def test_filters_non_approaching(self) -> None:
        approaching = _make_aircraft(icao24="app", baro_altitude=300, true_track=288)
        not_approaching = _make_aircraft(icao24="nope", baro_altitude=300, true_track=90)
        result = find_approaching([approaching, not_approaching])
        assert len(result) == 1
        assert result[0].icao24 == "app"


class TestGetNearby:
    def test_within_radius(self) -> None:
        close = _make_aircraft(latitude=52.404, longitude=16.864)
        result = get_nearby(
            aircraft=[close],
            radius_km=5.0,
        )
        assert len(result) == 1

    def test_outside_radius(self) -> None:
        far = _make_aircraft(latitude=53.0, longitude=17.0)
        result = get_nearby(
            aircraft=[far],
            radius_km=3.0,
        )
        assert len(result) == 0