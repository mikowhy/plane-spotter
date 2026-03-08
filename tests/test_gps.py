"""Tests for the gps module."""

import json
from pathlib import Path
from unittest.mock import patch

from planespotter.gps import DEFAULT_LAT, DEFAULT_LON, read_gps, save_config


def _read_gps_no_hardware(config_path: Path) -> tuple[float, float]:
    with (
        patch("planespotter.gps.CONFIG_PATH", config_path),
        patch.dict("sys.modules", {"gps3": None, "gps3.agps3": None}),
    ):
        return read_gps()


class TestReadGpsFallback:
    def test_falls_back_to_saved_config(self, tmp_path: Path) -> None:
        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps({"lat": 51.0, "lon": 17.0}))

        lat, lon = _read_gps_no_hardware(config_path)

        assert lat == 51.0
        assert lon == 17.0

    def test_falls_back_to_defaults_when_no_config(self, tmp_path: Path) -> None:
        config_path = tmp_path / "config.json"

        lat, lon = _read_gps_no_hardware(config_path)

        assert lat == DEFAULT_LAT
        assert lon == DEFAULT_LON

    def test_falls_back_to_defaults_on_invalid_json(self, tmp_path: Path) -> None:
        config_path = tmp_path / "config.json"
        config_path.write_text("not valid json")

        lat, lon = _read_gps_no_hardware(config_path)

        assert lat == DEFAULT_LAT
        assert lon == DEFAULT_LON

    def test_falls_back_to_defaults_on_missing_keys(self, tmp_path: Path) -> None:
        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps({"foo": "bar"}))

        lat, lon = _read_gps_no_hardware(config_path)

        assert lat == DEFAULT_LAT
        assert lon == DEFAULT_LON

    def test_saves_config_when_falling_back_to_defaults(self, tmp_path: Path) -> None:
        config_path = tmp_path / "config.json"

        _read_gps_no_hardware(config_path)

        assert config_path.exists()
        saved = json.loads(config_path.read_text())
        assert saved["lat"] == DEFAULT_LAT
        assert saved["lon"] == DEFAULT_LON


class TestSaveConfig:
    def test_writes_json(self, tmp_path: Path) -> None:
        config_path = tmp_path / "config.json"

        with patch("planespotter.gps.CONFIG_PATH", config_path):
            save_config(
                lat=52.0,
                lon=16.5,
            )

        saved = json.loads(config_path.read_text())
        assert saved["lat"] == 52.0
        assert saved["lon"] == 16.5