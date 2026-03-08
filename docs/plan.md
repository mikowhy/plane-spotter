# 🛫 Plane Spotter — Project Plan

## Context

An educational Raspberry Pi project. The goal is to build a browser-based dashboard that shows
a live camera stream pointed at the sky and real-time data about aircraft on approach to
Ławica Airport in Poznań (EPPO).

-----

## Project Owner

- **Location:** `52.403845, 16.863415` (Poznań, ~2.9km east of runway 28 threshold)
- **Python level:** Advanced
- **Goal:** General development + learning Web/API/hardware

-----

## Hardware

| Component            | Model / Description                          |
|----------------------|----------------------------------------------|
| Raspberry Pi         | Model B+ (micro USB, 2x USB, Ethernet, HDMI) |
| Camera               | Raspberry Pi Camera Rev 1.3 + FFC cable      |
| GPS                  | ANTEK BQ-V0 (UART: PPS, RXD, TXD, GND, VCC)  |
| GPIO Extension Board | T-shape, red, 40-pin                         |
| GPIO Ribbon Cable    | 40-pin flat ribbon cable                     |
| Jumper wires         | M-M/M-F set                                  |
| Breadboard           | Solderless, 400 holes                        |
| Power supply         | 5V micro USB (European plug)                 |
| WiFi                 | USB WiFi n adapter                           |
| Heatsinks            | 3 pcs (CPU, GPU, RAM)                        |
| Case                 | Acrylic, transparent                         |

-----

## Tech Stack

```
FastAPI + uvicorn    → async web server
picamera2           → camera control
gpsd + gps3         → GPS reading via UART
RPi.GPIO / gpiozero → GPIO pin control
SQLite / aiosqlite  → local database
httpx               → async HTTP client
Leaflet.js          → in-browser map (works offline)
OpenSky Network API → flight data (free, no key required)
```

-----

## Application Architecture

```
planespotter/
├── main.py          → entry point, manages asyncio
├── gpio.py          → status LED + button
├── camera.py        → stream and frame capture
├── gps.py           → coordinate reading (stationary)
├── flights.py       → polling OpenSky API for flights
├── matcher.py       → which plane is overhead right now?
├── database.py      → SQLite: flight history + snapshots
├── api.py           → FastAPI endpoints
└── templates/
    └── dashboard.html → frontend (Leaflet + stream + panel)
```

### API Endpoints

| Endpoint        | Description                     |
|-----------------|---------------------------------|
| `GET /stream`   | Live MJPEG stream from camera   |
| `GET /flights`  | Current nearby aircraft as JSON |
| `GET /location` | Home coordinates as GeoJSON     |
| `GET /history`  | Flight history from database    |
| `GET /`         | HTML dashboard                  |

### Dashboard (browser view)

- **Left side:** Live stream from camera pointing west (towards the airport)
- **Right side:** Leaflet map with aircraft icons + home + airport markers
- **Bottom:** Current flight panel: airline, flight number, origin→destination, aircraft type, altitude, speed
- **Notification:** when an aircraft enters ~3km radius from home

-----

## Ławica Airport (EPPO)

- **Coordinates:** `52.4205, 16.8310`
- **Runway:** 10/28 (true heading: 108°/288°)
- **Approach:** Aircraft most commonly land from the east, flying westbound (runway 28)
- **Observer position:** ~2.9km east of runway threshold — **ideal**
- **Aircraft altitude over home:** ~250–300m during approach

-----

## OpenSky Network API

- **URL:** `https://opensky-network.org/api/states/all`
- **Filter parameters:** `lamin`, `lamax`, `lomin`, `lomax` (bbox around Ławica)
- **Observation bbox:** lat: `52.35–52.50`, lon: `16.75–16.95`
- **No API key required** — free, 400 req/day anonymously
- **Data fields:** callsign, position, altitude, speed, heading, type (if available)

-----

## GPIO — Wiring Diagram

```
Status LED:
  GPIO 17 → 220Ω resistor → LED (+) → GND

Button:
  GPIO 27 → button → GND (internal pull-up)

GPS (UART):
  Pi TX (GPIO 14) → GPS RXD
  Pi RX (GPIO 15) → GPS TXD
  Pi 3.3V         → GPS VCC
  Pi GND          → GPS GND
```

-----

## Implementation Plan — 28 Steps

### PHASE 1 — Pi Setup (steps 1–4)

1. **Flash OS** — Raspberry Pi OS Legacy 32-bit via Raspberry Pi Imager (macOS)
- Hostname: `planespotter`
- SSH: enabled
- WiFi: configured in Imager
2. **First boot** — SSH: `ssh pi@planespotter.local`, system update
3. **Install libraries** — `picamera2`, `gpsd`, `gps3`, `fastapi`, `uvicorn`, `gpiozero`, `aiosqlite`, `httpx`
4. **Mount heatsinks** — attach to CPU/GPU/RAM before any extended testing

### PHASE 2 — Hardware (steps 5–8)

5. **GPIO Extension Board** — connect 40-pin ribbon cable between Pi and extension board
6. **LED + button** — wire up on breadboard, test `gpio.py`
7. **Camera** — connect FFC cable to CSI slot, test with `libcamera-still`
8. **GPS** — connect via UART, configure `gpsd`, test with `cgps`

### PHASE 3 — Python Modules (steps 9–14)

9. **`gpio.py`** — `StatusLED` class (blink, on, off) + `Button` with callback
10. **`camera.py`** — MJPEG frame generator + JPG save on event
11. **`gps.py`** — one-time coordinate read on startup, save to config file
12. **`flights.py`** — async polling OpenSky API every 15s, Ławica bbox filter
13. **`matcher.py`** — haversine distance, select aircraft closest to approach path
14. **`database.py`** — tables: `flights` (history), `snapshots` (images + flight_id)

### PHASE 4 — Web / API (steps 15–18)

15. **`api.py`** — base FastAPI app, mounting static files
16. **`GET /flights`** — returns JSON with current aircraft from `matcher.py`
17. **`GET /stream`** — StreamingResponse from MJPEG generator
18. **`GET /history`** — paginated history from SQLite

### PHASE 5 — Dashboard (steps 19–23)

19. **HTML skeleton** — two-column layout (stream | map + panel)
20. **Leaflet.js** — map with markers: home (🏠), airport (✈️), aircraft (icons)
21. **Live stream** — `<img src="/stream">` in left column
22. **Flight panel** — auto-refresh every 15s via `fetch('/flights')`, display data
23. **Notification** — JavaScript `Notification API` when aircraft < 3km away

### PHASE 6 — Integration (steps 24–25)

24. **`main.py`** — `asyncio.gather()` for: flight polling, FastAPI server, LED heartbeat
25. **systemd autostart** — `planespotter.service`, `WantedBy=multi-user.target`

### PHASE 7 — Polish (steps 26–28)

26. **Error handling** — no GPS → use saved coordinates; camera unavailable → placeholder
27. **Snapshots** — save JPG when aircraft enters bbox + save path in `database.py`
28. **Statistics** — `/stats` endpoint: daily flight count, top airlines, top routes

-----

## Implementation Notes

- Pi B+ has limited RAM (~512MB) — avoid buffering large video files
- MJPEG stream instead of H264 — simpler to implement, works in every browser
- Stationary GPS — read coordinates once on startup and save to `config.json`
- OpenSky API — if internet is unavailable, dashboard still works (stream + last known flights from cache)
- Leaflet.js can be loaded locally (offline) — pre-download OpenStreetMap tiles

-----

## Project Status

- [x] Plan approved
- [x] Hardware assembled
- [x] OS flashed to SD card
- [x] Pi configured and accessible via SSH
- [x] Modules implemented
- [x] Dashboard working (tested on Mac)
- [x] CI pipeline (GitHub Actions: lint, typecheck, tests)
- [x] Coding conventions documented and enforced
- [x] Pi: pip packages installed
- [x] Deployed and running on Pi (without camera/GPS hardware)
- [x] Camera connected and tested
- [x] GPS wired to matcher (reads position on startup, falls back to defaults)
- [x] Coding conventions enforced across all modules and tests
- [x] Favicon (plane SVG icon)
- [x] systemd autostart service (`planespotter.service`)
- [x] Test coverage: 42 tests (database, flights, matcher, gps, api)
- [ ] GPS connected and configured (gpsd) -- hardware
- [ ] LED + button tested on Pi -- hardware
- [ ] Snapshot capture on aircraft detection
- [ ] `/stats` endpoint (daily counts, top airlines)
