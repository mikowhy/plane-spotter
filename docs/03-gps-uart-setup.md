# Step 3 -- GPS + UART Setup

## Wiring (ANTEK BQ-V0)

```
Pi TX (GPIO 14) --> GPS RXD
Pi RX (GPIO 15) --> GPS TXD
Pi 3.3V         --> GPS VCC
Pi GND          --> GPS GND
```

## Pi B+ Advantage

The original B+ has no Bluetooth, so the PL011 UART (`/dev/ttyAMA0`) is directly available on GPIO 14/15. No need for `dtoverlay=disable-bt`.

## Enable UART

Edit `/boot/firmware/config.txt`:

```ini
enable_uart=1
```

## Disable Serial Console

The Linux console is attached to the serial port by default. Disable it so gpsd can use the port:

```bash
# Remove console=serial0,... from kernel command line
sudo sed -i 's/console=serial0,[0-9]* //g' /boot/firmware/cmdline.txt

# Disable serial-getty service
sudo systemctl stop serial-getty@ttyAMA0.service
sudo systemctl disable serial-getty@ttyAMA0.service
```

Reboot after these changes.

## Configure gpsd

Edit `/etc/default/gpsd`:

```
START_DAEMON="true"
GPSD_OPTIONS="-n"
DEVICES="/dev/ttyAMA0"
USBAUTO="false"
GPSD_SOCKET="/var/run/gpsd.sock"
```

The `-n` flag tells gpsd to poll immediately without waiting for a client.

```bash
sudo systemctl enable gpsd
sudo systemctl start gpsd
```

## Verify

```bash
cgps                     # interactive GPS monitor
cat /dev/ttyAMA0         # raw NMEA data
```

If no data appears, check baud rate (ANTEK BQ-V0 likely uses 9600):

```bash
stty -F /dev/ttyAMA0 9600
```