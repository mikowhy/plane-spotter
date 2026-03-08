import asyncio
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from planespotter import database
from planespotter.api import app, setup
from planespotter.camera import Camera
from planespotter.flights import Aircraft, FlightTracker


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


client = TestClient(app)


class TestDashboard:
    def test_returns_html(self) -> None:
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "Plane Spotter" in response.text


class TestLocationEndpoint:
    def test_returns_geojson(self) -> None:
        response = client.get("/location")
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "FeatureCollection"
        assert len(data["features"]) == 2

    def test_contains_home_and_airport(self) -> None:
        response = client.get("/location")
        data = response.json()
        names = [feature["properties"]["name"] for feature in data["features"]]
        assert "Home" in names
        assert "Lawica Airport (EPPO)" in names


class TestFlightsEndpoint:
    def test_returns_empty_when_no_tracker(self) -> None:
        setup(
            camera_instance=MagicMock(spec=Camera),
            tracker_instance=None,
        )
        response = client.get("/flights")
        assert response.status_code == 200
        data = response.json()
        assert data["aircraft"] == []
        assert data["approaching"] == []
        assert data["nearby"] == []

    def test_returns_aircraft_data(self) -> None:
        tracker = FlightTracker()
        tracker.aircraft = [
            _make_aircraft(
                icao24="abc123",
                callsign="LOT123",
            ),
        ]
        setup(
            camera_instance=MagicMock(spec=Camera),
            tracker_instance=tracker,
        )
        response = client.get("/flights")
        assert response.status_code == 200
        data = response.json()
        assert len(data["aircraft"]) == 1
        assert data["aircraft"][0]["icao24"] == "abc123"
        assert data["aircraft"][0]["callsign"] == "LOT123"


class TestStreamEndpoint:
    def test_returns_503_when_no_camera(self) -> None:
        setup(
            camera_instance=None,
            tracker_instance=MagicMock(spec=FlightTracker),
        )
        response = client.get("/stream")
        assert response.status_code == 503


class TestHistoryEndpoint:
    def test_returns_list(
        self,
        tmp_path: Path,
    ) -> None:
        db_path = tmp_path / "test.db"
        with patch.object(database, "DB_PATH", db_path):
            asyncio.run(database.init_db())
            response = client.get("/history")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
