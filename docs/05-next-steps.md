# Step 5 -- Next Steps Checklist

## On the Pi (hardware setup)

- [x] Finish `sudo apt upgrade -y`
- [x] Install system packages (see 01-pi-setup.md)
- [x] Create Python venv (see 01-pi-setup.md)
- [x] Install pip packages: `pip install .`
- [x] Mount heatsinks on CPU/GPU/RAM
- [x] Connect GPIO extension board + ribbon cable
- [x] Wire LED (GPIO 17 -> 220R -> LED -> GND) + button (GPIO 27 -> button -> GND)
- [ ] Test LED + button with `gpio.py`
- [x] Connect camera FFC cable, test with `rpicam-still` (see 02-camera-setup.md)
- [x] Camera streaming works in the app (`io.BufferedIOBase` fix applied)
- [ ] Connect GPS via UART, configure gpsd, test with `cgps` (see 03-gps-uart-setup.md)

## On Mac (code development)

Can be done in parallel -- no hardware needed:

- [x] Project scaffolding: `.gitignore`, `requirements.txt`, directory structure
- [x] `flights.py` -- OpenSky API polling (see 04-opensky-api.md)
- [x] `matcher.py` -- haversine distance + approach path matching
- [x] `database.py` -- SQLite schema (flights + snapshots tables)
- [x] `gpio.py` -- with stub/mock for non-Pi environments
- [x] `camera.py` -- with stub for non-Pi environments
- [x] `gps.py` -- one-time coordinate read, fallback to config file
- [x] `api.py` -- FastAPI endpoints
- [x] `main.py` -- asyncio entry point
- [x] `templates/dashboard.html` -- Leaflet map + stream + flight panel
- [x] Tested locally on Mac -- dashboard + OpenSky API working
- [x] Favicon -- plane SVG icon at `/favicon.ico`
- [x] GPS coordinates wired to matcher (`set_home()` called on startup)
- [x] Coding conventions enforced across all modules and tests
- [x] Test coverage: 42 tests (database, flights, matcher, gps, api)

## Remaining

- [ ] **Test LED + button** on the Pi
- [ ] **Connect GPS** via UART, configure gpsd, test with `cgps` (see 03-gps-uart-setup.md)
- [x] **systemd autostart** -- `planespotter.service` created (see 07-systemd-autostart.md)
- [ ] **Snapshot capture** -- save JPG when aircraft enters alert radius, store path in database
- [ ] **`/stats` endpoint** -- daily flight count, top airlines, top routes
