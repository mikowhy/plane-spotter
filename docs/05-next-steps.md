# Step 5 -- Next Steps Checklist

## On the Pi (hardware setup)

- [x] Finish `sudo apt upgrade -y`
- [x] Install system packages (see 01-pi-setup.md)
- [x] Create Python venv (see 01-pi-setup.md)
- [ ] Install pip packages: `pip install .` (in progress)
- [ ] Mount heatsinks on CPU/GPU/RAM
- [ ] Connect GPIO extension board + ribbon cable
- [ ] Wire LED (GPIO 17 -> 220R -> LED -> GND) + button (GPIO 27 -> button -> GND)
- [ ] Test LED + button with `gpio.py`
- [ ] Connect camera FFC cable, test with `rpicam-still` (see 02-camera-setup.md)
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

## Suggested Order

1. Pi: install packages + venv (while upgrade runs)
2. Mac: scaffolding + `flights.py` + `matcher.py` (no hardware deps)
3. Pi: heatsinks + camera + GPS wiring
4. Mac: `database.py` + `api.py` + `dashboard.html`
5. Pi: test hardware modules
6. Deploy code to Pi:
   ```bash
   git clone https://github.com/mikowhy/plane-spotter.git /home/pi/plane-spotter
   cd /home/pi/plane-spotter
   source /home/pi/planespotter-env/bin/activate
   pip install .
   ```
7. Integrate and test end-to-end