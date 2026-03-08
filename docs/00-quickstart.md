# Step 0 -- Quick Start Guide

How to run the Plane Spotter app — on the Pi or locally on your Mac for development.

## 1. Power On

1. Insert the SD card (with Raspberry Pi OS already flashed)
2. Connect Ethernet cable (or ensure WiFi is configured)
3. Plug in the 5V micro USB power supply
4. Wait ~30 seconds for the Pi to boot

## 2. Connect via SSH

From your Mac (on the same network):

```bash
ssh pi@planespotter.local
```

> If `planespotter.local` doesn't resolve, find the Pi's IP from your router admin page and use `ssh pi@<ip>`.

## 3. Get the Code

**First time:**

```bash
cd /home/pi
git clone https://github.com/mikowhy/plane-spotter.git
cd plane-spotter
```

**Returning (pull latest changes):**

```bash
cd /home/pi/plane-spotter
git pull
```

## 4. Activate the Virtual Environment

```bash
source /home/pi/planespotter-env/bin/activate
```

You should see `(planespotter-env)` in your prompt.

> If the venv doesn't exist yet, see `docs/01-pi-setup.md` to create it and install dependencies.

## 5. Run the App

```bash
cd /home/pi/plane-spotter
python -m planespotter.main
```

You should see output like:

```
2026-03-08 12:00:00 [planespotter.gps] INFO: Observer position: 52.403845, 16.863415
2026-03-08 12:00:00 [planespotter.main] INFO: Started
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## 6. Open the Dashboard

On your Mac, open a browser and go to:

```
http://planespotter.local:8000/
```

You should see the live dashboard with the camera stream (or placeholder) and the Leaflet map.

## 7. Stop the App

Press `Ctrl+C` in the SSH terminal.

## 8. Shut Down the Pi

Always shut down properly — pulling the power cable can corrupt the SD card.

```bash
sudo shutdown -h now
```

Wait until the green LED on the Pi stops blinking (about 10 seconds), then unplug the power cable.

---

## Running Locally (Mac / localhost)

You can run the app on your Mac for development — camera and GPS will use fallback stubs automatically.

### 1. Clone and enter the repo

```bash
git clone https://github.com/mikowhy/plane-spotter.git
cd plane-spotter
```

### 2. Create a virtual environment and install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### 3. Run the app

```bash
python -m planespotter.main
```

### 4. Open the dashboard

```
http://localhost:8000/
```

> Camera shows a placeholder image (no `picamera2` on Mac). GPS falls back to default coordinates (Poznan). Flight data works normally via OpenSky API.

---

## Troubleshooting

| Problem                              | Fix                                                                 |
|--------------------------------------|---------------------------------------------------------------------|
| `ssh: Could not resolve hostname`    | Use the Pi's IP address instead of `planespotter.local`             |
| `ModuleNotFoundError`                | Make sure the venv is activated (step 4)                            |
| `Address already in use` (port 8000) | Another instance is running — kill it: `pkill -f planespotter.main` |
| No camera stream (placeholder shown) | Camera not connected — this is expected, the app runs without it    |
| GPS timeout (falls back to defaults) | GPS not connected — this is expected, uses saved coordinates        |
