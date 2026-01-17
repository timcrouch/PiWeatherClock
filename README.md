# WeatherClock Pi

A dedicated weather and time display application for Raspberry Pi 5 with touchscreen support.

![WeatherClock Pi](assets/icons/sunny_day.png)

## Features

- **Real-time Date & Time Display** - Large, readable clock with configurable 12h/24h format
- **Current Weather** - Temperature, feels-like temperature, and weather condition with icons
- **5-Day Forecast** - Touch the temperature area to view extended forecast
- **Auto-Refresh** - Weather data updates every 15 minutes (configurable)
- **Offline Resilient** - Caches weather data for offline viewing
- **Kiosk Mode** - Fullscreen operation with hidden cursor
- **Dark Theme** - Easy on the eyes for 24/7 operation

## Requirements

### Hardware

- Raspberry Pi 5 (4GB or 8GB RAM recommended)
- Touchscreen display (800x480 minimum resolution)
- Network connection (WiFi or Ethernet)
- Official 27W USB-C power supply

### Software

- Raspberry Pi OS (64-bit) - Bookworm or later
- Python 3.11+
- Tkinter (included with Python on Raspberry Pi OS)

## Installation

### 1. Clone or Copy the Application

```bash
# Clone via git
git clone <repository-url> ~/weatherclock

# Or copy the files manually to ~/weatherclock
```

### 2. Install Dependencies

```bash
cd ~/weatherclock
pip3 install -r requirements.txt
```

### 3. Configure the Application

```bash
# Create config directory
mkdir -p ~/.config/weatherclock

# Copy example configuration
cp config.yaml.example ~/.config/weatherclock/config.yaml

# Edit configuration
nano ~/.config/weatherclock/config.yaml
```

Configure your location (coordinates can be found via Google Maps):

```yaml
location:
  latitude: 40.7128
  longitude: -74.0060
  name: "New York, NY"

display:
  temperature_unit: "fahrenheit"  # or "celsius"
  time_format: "12h"              # or "24h"
  show_seconds: true
  theme: "dark"                   # or "light"
```

If you leave the location coordinates as `null`, the application will attempt to auto-detect your location via IP address.

### 4. Test the Application

```bash
# Run in windowed mode for testing
python3 main.py --windowed

# Run in fullscreen
python3 main.py
```

**Keyboard Shortcuts:**
- `Escape` - Exit fullscreen mode (or quit if already windowed)

## Auto-Start on Boot

### Using systemd (Recommended)

1. Create a service file:

```bash
sudo nano /etc/systemd/system/weatherclock.service
```

2. Add the following content:

```ini
[Unit]
Description=WeatherClock Pi Display
After=graphical.target

[Service]
Environment=DISPLAY=:0
ExecStart=/usr/bin/python3 /home/pi/weatherclock/main.py
Restart=always
RestartSec=10
User=pi

[Install]
WantedBy=graphical.target
```

3. Enable and start the service:

```bash
sudo systemctl enable weatherclock.service
sudo systemctl start weatherclock.service
```

### Disable Screen Blanking

To prevent the screen from turning off:

```bash
# Add to ~/.config/lxsession/LXDE-pi/autostart
@xset s off
@xset -dpms
@xset s noblank
```

## Command Line Options

```
python3 main.py [OPTIONS]

Options:
  -w, --windowed     Run in windowed mode instead of fullscreen
  -c, --show-cursor  Show the mouse cursor
  -d, --debug        Enable debug logging
  -f, --config PATH  Path to configuration file
```

## Weather Data

WeatherClock Pi uses the **Open-Meteo API** for weather data:
- Free to use (no API key required)
- Global coverage with 1km resolution
- Updates every 15 minutes (configurable)

## Project Structure

```
weatherclock/
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── config.yaml.example        # Example configuration
├── README.md                  # This file
├── gui/
│   ├── display.py             # Main application class
│   ├── main_view.py           # Main display view
│   ├── forecast_view.py       # 5-day forecast view
│   └── widgets.py             # Custom UI widgets
├── services/
│   ├── weather.py             # Weather API client
│   └── location.py            # Location detection
├── models/
│   └── weather_data.py        # Data structures
├── utils/
│   ├── config.py              # Configuration management
│   ├── icons.py               # Icon loading utilities
│   └── logging_config.py      # Logging setup
└── assets/
    └── icons/                 # Weather icons
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Application won't start | Check Python version: `python3 --version` (needs 3.11+) |
| No weather data | Verify internet connection, check logs at `~/.local/log/weatherclock/` |
| Touch not working | Verify touchscreen is detected: `xinput list` |
| Icons not loading | Verify icons exist in `assets/icons/` directory |
| High CPU usage | Reduce update frequency in config, disable seconds display |

## Logs

Application logs are stored at:
```
~/.local/log/weatherclock/app.log
```

View logs:
```bash
tail -f ~/.local/log/weatherclock/app.log
```

## License

MIT License - Feel free to use and modify for personal or commercial use.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.
