# Step 1 -- Raspberry Pi Setup

## System Update (done)

```bash
sudo systemctl stop packagekit
sudo apt update && sudo apt upgrade -y
```

## Install System Packages

```bash
# Camera and libcamera
sudo apt install -y python3-picamera2 libcamera-apps

# GPS daemon
sudo apt install -y gpsd gpsd-clients

# Python dev + venv
sudo apt install -y python3-dev python3-venv python3-pip
```

> `python3-picamera2` is pre-installed on full Raspberry Pi OS but may be missing on Lite.

## Create Python Virtual Environment

Bookworm blocks global pip installs (PEP 668). Use a venv with `--system-site-packages` so apt-installed `picamera2` and `libcamera` are visible:

```bash
python3 -m venv --system-site-packages /home/pi/planespotter-env
source /home/pi/planespotter-env/bin/activate
pip install fastapi "uvicorn[standard]" gps3 gpiozero aiosqlite httpx jinja2
```

> Do NOT pip install picamera2 -- the apt version must match system libcamera.

## User Permissions

Verify the `pi` user has the required groups:

```bash
groups pi
# Should include: video gpio dialout
# Add if missing:
sudo usermod -aG video,gpio,dialout pi
```

## Pi B+ Gotchas (512MB RAM, single-core ARMv6)

- Use exactly 1 uvicorn worker
- MJPEG stream at 640x480, 10-15 fps max
- Use `MJPEGEncoder` (hardware) -- halves CPU vs software encoder
- Consider adding swap:
  ```bash
  sudo dphys-swapfile swapoff
  sudo sed -i 's/CONF_SWAPSIZE=.*/CONF_SWAPSIZE=256/' /etc/dphys-swapfile
  sudo dphys-swapfile setup && sudo dphys-swapfile swapon
  ```