"""SQLite database for flight history and snapshots."""

import aiosqlite
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "planespotter.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS flights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    icao24 TEXT NOT NULL,
    callsign TEXT,
    origin_country TEXT,
    first_seen TEXT DEFAULT (datetime('now')),
    last_seen TEXT DEFAULT (datetime('now')),
    min_altitude REAL,
    min_distance REAL,
    on_approach INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    flight_id INTEGER REFERENCES flights(id),
    path TEXT NOT NULL,
    taken_at TEXT DEFAULT (datetime('now'))
);
"""


async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(SCHEMA)
        await db.commit()
    logger.info("Database initialized at %s", DB_PATH)


async def log_flight(
    icao24: str,
    callsign: str | None,
    origin_country: str,
    altitude: float | None,
    distance: float | None,
    on_approach: bool,
) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        # Update existing flight if seen recently, otherwise insert new
        cursor = await db.execute(
            """SELECT id FROM flights
               WHERE icao24 = ? AND last_seen > datetime('now', '-5 minutes')
               ORDER BY last_seen DESC LIMIT 1""",
            (icao24,),
        )
        row = await cursor.fetchone()

        if row:
            flight_id = row[0]
            await db.execute(
                """UPDATE flights SET
                   last_seen = datetime('now'),
                   min_altitude = MIN(min_altitude, ?),
                   min_distance = MIN(min_distance, ?)
                   WHERE id = ?""",
                (altitude, distance, flight_id),
            )
        else:
            cursor = await db.execute(
                """INSERT INTO flights (icao24, callsign, origin_country, min_altitude, min_distance, on_approach)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (icao24, callsign, origin_country, altitude, distance, int(on_approach)),
            )
            flight_id = cursor.lastrowid

        await db.commit()
        return flight_id


async def save_snapshot(flight_id: int, path: str) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO snapshots (flight_id, path) VALUES (?, ?)",
            (flight_id, path),
        )
        await db.commit()


async def get_history(limit: int = 50, offset: int = 0) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """SELECT id, icao24, callsign, origin_country, first_seen, last_seen,
                      min_altitude, min_distance, on_approach
               FROM flights ORDER BY last_seen DESC LIMIT ? OFFSET ?""",
            (limit, offset),
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]