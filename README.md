# 🍄 MushroomsFarm

Monitor and control your mushroom farm using a Raspberry Pi. The system reads temperature and humidity from an SHT31 sensor, automatically controls a USB humidifier via GPIO, streams a live camera feed, and exposes everything through a local web dashboard.

## Hardware

| Component | Details |
|---|---|
| Board | Raspberry Pi (tested on Pi 3/4) |
| Sensor | SHT31 (I2C, address `0x44`, bus 1) |
| Humidifier | USB power switch module via GPIO pins 26 (power) and 13 (trigger) |
| Camera | Raspberry Pi Camera Module (Picamera2) |

## Software Requirements

Install dependencies on the Pi:

```bash
pip install RPi.GPIO smbus picamera2
```

## Project Structure

```
├── main.py                  # Entry point — starts all subsystems
├── abs_worker.py            # Abstract base class for threaded workers
├── shared_data.py           # Thread-safe sensor data container
├── sht31.py                 # SHT31 temperature/humidity sensor reader
├── moisture_controller.py   # GPIO humidifier controller
├── httpserver.py            # HTTP API server (port 8080)
├── camera.py                # MJPEG camera stream server (port 8000)
├── gpio_pins_distribution.py
└── web/
    └── index.html           # Web dashboard (open in any browser)
```

## Network Setup

The Pi is assigned a static IP. To configure it (example using NetworkManager on Pi OS Bookworm):

```bash
# Find your connection name
sudo nmcli -p connection show

# Set static IP (replace "Oxio" with your connection name)
sudo nmcli c mod "Oxio" ipv4.addresses 192.168.4.45/24 ipv4.method manual
sudo nmcli c mod "Oxio" ipv4.gateway 192.168.0.1
sudo nmcli c mod "Oxio" ipv4.dns "8.8.8.8,8.8.4.4"
sudo reboot
```

Reference: [Set a static IP on Pi OS Bookworm](https://www.abelectronics.co.uk/kb/article/31/set-a-static-ip-address-on-raspberry-pi-os-bookworm)

## Deploying to the Pi

Copy all Python files to the Pi:

```bash
scp *.py yurii@192.168.4.45:/home/yurii/controller
scp web/index.html yurii@192.168.4.45:/home/yurii/controller/web/
```

SSH in:

```bash
ssh yurii@192.168.4.45
```

## Running

Start the controller from the Pi:

```bash
cd /home/yurii/controller
python main.py
```

This launches four concurrent subsystems:

- **SHT31** — reads temperature and humidity every ~1.5 s and stores results in shared memory
- **MoistureController** — checks humidity every second; turns the humidifier on if below 90%, off if at or above 90%
- **Camera** — streams MJPEG video on port `8000` at `/camera`
- **HttpServer** — serves the REST API on port `8080`

Stop with `Ctrl+C` or `kill` (SIGTERM is handled cleanly).

## HTTP API

Base URL: `http://192.168.4.45:8080`

| Method | Path | Description |
|---|---|---|
| GET | `/status` | JSON: `{ temp_c, humd, moisturizer_on }` |
| GET | `/temp` | Plain text: current temperature in °C |
| GET | `/humd` | Plain text: current humidity in % |
| POST | `/humd/start` | Turn humidifier on manually |
| POST | `/humd/stop` | Turn humidifier off manually |

Example:

```bash
curl http://192.168.4.45:8080/status
# {"temp_c": 22, "humd": 85, "moisturizer_on": true}
```

Camera stream URL: `http://192.168.4.45:8000/camera` (MJPEG, compatible with `<img>` tags and VLC)

## Web Dashboard

Open `web/index.html` in any browser on the same network — no server needed, it's a static file.

The dashboard shows:
- Live camera feed
- Current temperature and humidity
- Humidifier status (auto-updated every 2 s)
- Manual **Turn On / Turn Off** buttons

If the Pi is unreachable, an error banner appears automatically.

> **Note:** The `BASE` URL in `web/index.html` is hardcoded to `http://192.168.4.45`. Update it if your Pi's IP changes.

## Humidifier Logic

The controller targets **90–100% relative humidity**. The logic runs in its own thread:

- humidity < 90% → humidifier turns **on**
- humidity ≥ 90% → humidifier turns **off**

Manual overrides via the web UI or HTTP API take effect immediately but will be corrected on the next automatic cycle (~1 s).

## References

- [SHT31 example code](https://github.com/machineshopuk/SHT31/blob/master/SHT31.py)
- [USB Power Switch Module](https://thepihut.com/products/usb-power-switch-module)
- [Static IP on Pi OS Bookworm](https://www.abelectronics.co.uk/kb/article/31/set-a-static-ip-address-on-raspberry-pi-os-bookworm)
