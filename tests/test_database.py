from pathlib import Path

import pytest

import planespotter.database as db_mod
from planespotter.database import get_history, init_db, log_flight


@pytest.fixture(autouse=True)
def use_temp_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(db_mod, "DB_PATH", tmp_path / "test.db")


async def test_init_db() -> None:
    await init_db()


async def test_log_flight_insert() -> None:
    await init_db()
    flight_id = await log_flight(
        icao24="abc123",
        callsign="TEST1",
        origin_country="Poland",
        altitude=300.0,
        distance=2.5,
        on_approach=True,
    )
    assert flight_id is not None
    assert flight_id > 0


async def test_log_flight_update() -> None:
    await init_db()
    id1 = await log_flight(
        icao24="abc123",
        callsign="TEST1",
        origin_country="Poland",
        altitude=300.0,
        distance=2.5,
        on_approach=True,
    )
    id2 = await log_flight(
        icao24="abc123",
        callsign="TEST1",
        origin_country="Poland",
        altitude=250.0,
        distance=2.0,
        on_approach=True,
    )
    assert id1 == id2


async def test_get_history() -> None:
    await init_db()
    await log_flight(
        icao24="abc123",
        callsign="TEST1",
        origin_country="Poland",
        altitude=300.0,
        distance=2.5,
        on_approach=True,
    )
    await log_flight(
        icao24="def456",
        callsign="TEST2",
        origin_country="Germany",
        altitude=500.0,
        distance=4.0,
        on_approach=False,
    )
    history = await get_history(limit=10)
    assert len(history) == 2
    assert history[0]["icao24"] in ("abc123", "def456")


async def test_get_history_empty() -> None:
    await init_db()
    history = await get_history()
    assert history == []
