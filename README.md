# Plane Spotter

A Raspberry Pi-based dashboard that shows a live camera stream pointed at the sky and real-time data about aircraft on approach to Lawica Airport in Poznan (EPPO).

## Hardware

- Raspberry Pi Model B+
- Raspberry Pi Camera Rev 1.3
- ANTEK BQ-V0 GPS module (UART)
- Status LED + button on GPIO

## Tech Stack

- **Backend:** FastAPI + uvicorn (async)
- **Camera:** picamera2 with hardware MJPEG encoder
- **GPS:** gpsd + gps3
- **Flight data:** OpenSky Network API
- **Frontend:** Leaflet.js map + live MJPEG stream
- **Database:** SQLite (flight history + snapshots)

## Setup

On the Raspberry Pi:

```bash
git clone https://github.com/mikowhy/plane-spotter.git /home/pi/plane-spotter
cd /home/pi/plane-spotter
python3 -m venv --system-site-packages /home/pi/planespotter-env
source /home/pi/planespotter-env/bin/activate
pip install .
```

See `docs/` for detailed setup guides.

## Development

Install dev dependencies:

```bash
pip install ".[dev]"
```

Run tests:

```bash
pytest tests/ -v
```

Run linters:

```bash
black --check planespotter/ tests/
isort --check planespotter/ tests/
mypy planespotter/
```

## CI

GitHub Actions runs lint, type check, and tests on every push and PR to `main`. See `.github/workflows/ci.yml`.