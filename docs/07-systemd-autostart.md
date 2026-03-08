# Step 7 -- systemd Autostart

## Install the Service

Copy the service file to systemd:

```bash
sudo cp /home/pi/plane-spotter/planespotter.service /etc/systemd/system/
sudo systemctl daemon-reload
```

## Enable (start on boot)

```bash
sudo systemctl enable planespotter
```

## Start / Stop / Restart

```bash
sudo systemctl start planespotter
sudo systemctl stop planespotter
sudo systemctl restart planespotter
```

## Check Status

```bash
sudo systemctl status planespotter
```

## View Logs

```bash
# Follow live logs
journalctl -u planespotter -f

# Last 50 lines
journalctl -u planespotter -n 50

# Logs since last boot
journalctl -u planespotter -b
```

## Uninstall

```bash
sudo systemctl stop planespotter
sudo systemctl disable planespotter
sudo rm /etc/systemd/system/planespotter.service
sudo systemctl daemon-reload
```