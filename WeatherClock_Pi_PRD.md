# Product Requirements Document: WeatherClock Pi

**Raspberry Pi 5 Weather & Time Display Application**

| Document Info | Details |
|---------------|---------|
| Version | 1.0 |
| Date | 2026-01-17 |
| Status | Draft |
| Platform | Raspberry Pi 5 |

---

## Table of Contents

1. Executive Summary
2. Product Overview
3. Technical Requirements
4. API Selection & Integration
5. Functional Requirements
6. User Interface Specifications
7. System Architecture
8. Data Models
9. Implementation Guide
10. Testing Requirements
11. Deployment Guide
12. Maintenance & Support
13. Future Enhancements
- Appendix A: API Reference
- Appendix B: Hardware Setup
- Appendix C: Troubleshooting

---

## 1. Executive Summary

WeatherClock Pi is a dedicated weather and time display application designed for Raspberry Pi 5 with touchscreen capability. The application provides at-a-glance weather information including current temperature, feels-like temperature, and weather conditions, alongside accurate time and date display.

The application leverages free, open APIs to retrieve weather data without requiring paid subscriptions or API keys with usage limits. The touch-enabled interface allows users to interact with the display to view extended 5-day forecasts.

### 1.1 Key Features

- Real-time date and time display with automatic synchronization
- Current temperature with actual and feels-like readings
- Weather condition display (sunny, cloudy, rain, snow) with icons
- Touch-activated 5-day forecast view
- Horizontal (landscape) display orientation
- Auto-start on boot with kiosk mode operation

### 1.2 Target Users

Home users seeking a dedicated weather display for kitchen, bedroom, or office environments. The application is designed for 24/7 operation as an always-on information display.

---

## 2. Product Overview

### 2.1 Problem Statement

Users want quick, glanceable access to current time and weather conditions without needing to check phones or computers. Existing solutions often require subscriptions, have privacy concerns, or lack customization options.

### 2.2 Solution

A self-hosted, privacy-respecting weather display that runs on affordable Raspberry Pi hardware. The application uses free APIs, requires no accounts or subscriptions, and provides a clean, modern interface optimized for touchscreen interaction.

### 2.3 Success Criteria

- Display updates weather data every 15 minutes automatically
- Time display accurate to within 1 second via NTP synchronization
- Touch response time under 100ms
- Application runs continuously for 30+ days without restart
- Memory usage remains stable (no memory leaks)

---

## 3. Technical Requirements

### 3.1 Hardware Requirements

| Component | Specification |
|-----------|---------------|
| Computer | Raspberry Pi 5 (4GB or 8GB RAM recommended) |
| Operating System | Raspberry Pi OS (64-bit) - Bookworm or later |
| Display | Official Raspberry Pi Touch Display or compatible touchscreen (800x480 minimum) |
| Storage | 16GB+ microSD card (Class 10 or better) |
| Network | Wi-Fi or Ethernet connection required |
| Power | Official Raspberry Pi 5 27W USB-C Power Supply |

### 3.2 Software Requirements

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.11+ | Primary application language |
| Tkinter | 8.6+ | GUI framework (included with Python) |
| Pillow | 10.0+ | Image processing for weather icons |
| Requests | 2.31+ | HTTP client for API calls |
| python-dateutil | 2.8+ | Date/time parsing and manipulation |
| PyYAML | 6.0+ | Configuration file parsing |

### 3.3 Display Requirements

- Minimum resolution: 800x480 pixels
- Recommended resolution: 1024x600 or 1280x800 pixels
- Orientation: **Landscape (horizontal) - MANDATORY**
- Touch capability: Single-point capacitive or resistive touch
- Viewing angle: IPS panel recommended for wide viewing angles

---

## 4. API Selection & Integration

### 4.1 Weather API: Open-Meteo

Open-Meteo is selected as the primary weather data provider due to its completely free tier, no API key requirement, and comprehensive data coverage.

**API Base URL:** `https://api.open-meteo.com/v1/forecast`

#### 4.1.1 API Features

| Feature | Details |
|---------|---------|
| Cost | Free for non-commercial use (no API key required) |
| Rate Limit | 10,000 requests/day (more than sufficient) |
| Data Points | Temperature, feels-like, weather code, humidity, wind |
| Forecast Range | Up to 16 days (we use 5 days) |
| Update Frequency | Hourly model updates |
| Coverage | Global coverage with 1km resolution |

#### 4.1.2 Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| latitude | float | Geographic latitude (-90 to 90) |
| longitude | float | Geographic longitude (-180 to 180) |
| current | string[] | Current weather variables to retrieve |
| daily | string[] | Daily forecast variables to retrieve |
| temperature_unit | string | celsius or fahrenheit |
| timezone | string | Timezone for timestamps (e.g., America/New_York) |
| forecast_days | integer | Number of forecast days (1-16) |

#### 4.1.3 Example API Request

```
GET https://api.open-meteo.com/v1/forecast?latitude=40.7128&longitude=-74.0060&current=temperature_2m,apparent_temperature,weather_code,is_day&daily=weather_code,temperature_2m_max,temperature_2m_min&temperature_unit=fahrenheit&timezone=America/New_York&forecast_days=5
```

### 4.2 Time Synchronization

The application uses the system clock, which should be synchronized via NTP (Network Time Protocol). Raspberry Pi OS automatically handles NTP synchronization when connected to the internet.

- **Primary NTP Servers:** pool.ntp.org (default in Raspberry Pi OS)
- **Fallback:** time.google.com, time.cloudflare.com

No external time API is required as the system clock provides accurate time when NTP is properly configured.

### 4.3 Geolocation (Optional)

For automatic location detection, the application can use the IP-API service:

**API URL:** `http://ip-api.com/json/`

This free service provides approximate location based on IP address. Users can also manually configure their location coordinates in a configuration file.

---

## 5. Functional Requirements

### 5.1 Main Display View (FR-001)

**Description:** The primary view showing current time, date, temperature, and weather condition.

#### 5.1.1 Time Display

- Display current time in large, readable format (HH:MM:SS or HH:MM)
- Support both 12-hour (with AM/PM) and 24-hour formats (configurable)
- Update every second for seconds display, or every minute if seconds hidden
- Font size: Minimum 72pt for visibility across room

#### 5.1.2 Date Display

- Display current date with day of week
- Format: "Saturday, January 17, 2026" (configurable)
- Update at midnight automatically

#### 5.1.3 Temperature Display

- Display actual temperature prominently (e.g., "45°F" or "7°C")
- Display feels-like temperature below or beside actual (e.g., "Feels like 38°F")
- Support Fahrenheit and Celsius (configurable)
- **Temperature area is touch-sensitive (triggers forecast view)**
- Visual indicator showing the area is tappable

#### 5.1.4 Weather Condition Display

- Display weather icon representing current condition
- Display text label for condition (e.g., "Sunny", "Cloudy", "Rain", "Snow")
- Icon size: Minimum 64x64 pixels, recommended 128x128 pixels

### 5.2 Weather Condition Mapping (FR-002)

Open-Meteo uses WMO weather codes. The application must map these to the four primary conditions:

| Condition | WMO Codes | Description |
|-----------|-----------|-------------|
| Sunny/Clear | 0, 1 | Clear sky, mainly clear |
| Cloudy | 2, 3, 45, 48 | Partly cloudy, overcast, fog, depositing rime fog |
| Rain | 51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82, 95, 96, 99 | Drizzle, rain, freezing rain, showers, thunderstorm |
| Snow | 71, 73, 75, 77, 85, 86 | Snow fall, snow grains, snow showers |

### 5.3 Five-Day Forecast View (FR-003)

**Trigger:** User touches/taps the temperature display area

**Behavior:** Overlay or transition to forecast view

#### 5.3.1 Forecast Display Requirements

- Show 5 days including today
- Each day displays: Day name, weather icon, high temperature, low temperature
- Horizontal layout with days arranged left to right
- Today should be visually highlighted or labeled
- Touch anywhere to return to main view

#### 5.3.2 Auto-Return Behavior

- Automatically return to main view after 30 seconds of inactivity (configurable)
- Display countdown timer or progress indicator (optional)

### 5.4 Data Refresh (FR-004)

- Weather data refresh interval: Every 15 minutes (configurable, minimum 5 minutes)
- Display last update timestamp (optional, can be hidden)
- Visual indicator during data refresh (subtle loading spinner)
- Graceful handling of API failures (show cached data with warning)
- Retry logic: 3 attempts with exponential backoff (5s, 15s, 45s)

### 5.5 Error Handling (FR-005)

| Error Condition | Handling |
|-----------------|----------|
| No internet connection | Display cached data with "Offline" indicator, retry every 60 seconds |
| API request timeout | Retry with backoff, show last known data |
| Invalid API response | Log error, continue with cached data, alert after 3 consecutive failures |
| Location not configured | Attempt auto-detection, prompt for manual entry if failed |
| Display/GUI error | Log error, attempt restart, show minimal fallback view |

---

## 6. User Interface Specifications

### 6.1 Layout Overview

The interface uses a horizontal (landscape) layout divided into distinct zones for optimal readability and touch interaction.

- **Screen Orientation:** Landscape (horizontal) - MANDATORY
- **Target Resolution:** 800x480 (minimum) to 1920x1080 (maximum)
- **Aspect Ratio:** 16:9 or 16:10 preferred

### 6.2 Main View Layout

The main view is divided into a grid layout with three primary sections arranged horizontally:

| Zone | Position | Width % | Content |
|------|----------|---------|---------|
| Time Zone | Left | 45% | Current time (large), current date (below time) |
| Weather Zone | Center-Right | 30% | Weather icon, condition text, location name |
| Temperature Zone | Right | 25% | Current temp (large), feels-like temp (smaller), touch target |

### 6.3 Visual Design Specifications

#### 6.3.1 Color Scheme (Dark Theme - Default)

| Element | Color | Hex Value |
|---------|-------|-----------|
| Background | Dark Gray | #1a1a2e |
| Primary Text | White | #ffffff |
| Secondary Text | Light Gray | #b0b0b0 |
| Accent Color | Blue | #4fc3f7 |
| Touch Highlight | Light Blue | #81d4fa with 30% opacity |
| Warning/Error | Orange/Red | #ff9800 / #f44336 |

#### 6.3.2 Typography

| Element | Font Size | Font Weight |
|---------|-----------|-------------|
| Time (HH:MM) | 96-144px | Bold (700) |
| Time Seconds | 48-72px | Regular (400) |
| Date | 24-32px | Regular (400) |
| Current Temperature | 64-96px | Bold (700) |
| Feels Like | 18-24px | Regular (400) |
| Condition Text | 24-32px | Medium (500) |
| Forecast Day | 18-24px | Medium (500) |
| Forecast Temps | 20-28px | Regular (400) |

- **Primary Font:** Roboto or system sans-serif font
- **Fallback Fonts:** Arial, Helvetica, sans-serif

### 6.4 Touch Interaction Design

- Minimum touch target size: 48x48 pixels (following accessibility guidelines)
- Temperature zone should have visible border or background indicating it is interactive
- Touch feedback: Brief color change or scale animation on tap
- Debounce touch events to prevent accidental double-taps
- In forecast view, entire screen is touch target to return to main view

### 6.5 Forecast View Layout

The 5-day forecast displays horizontally with equal-width columns:

- Each day occupies 20% of screen width
- Vertical arrangement within each day: Day name → Icon → High temp → Low temp
- Today column has highlighted background or border
- "Tap anywhere to return" hint at bottom of screen
- Optional: Progress bar showing auto-return countdown

### 6.6 Weather Icons

The application includes a set of weather icons for each condition:

| Condition | Day Icon | Night Icon (Optional) |
|-----------|----------|----------------------|
| Sunny/Clear | Sun symbol | Moon with stars |
| Cloudy | Cloud | Cloud with moon |
| Rain | Cloud with raindrops | Same as day |
| Snow | Cloud with snowflakes | Same as day |

- **Icon Format:** SVG (preferred) or PNG with transparency
- **Icon Sizes:** 128x128 (main view), 64x64 (forecast view)

---

## 7. System Architecture

### 7.1 Application Components

The application follows a modular architecture with clear separation of concerns:

| Component | Responsibility |
|-----------|----------------|
| main.py | Application entry point, initialization, main loop |
| gui/display.py | Tkinter GUI implementation, layout management, rendering |
| gui/widgets.py | Custom widget classes (TimeWidget, TempWidget, ForecastWidget) |
| services/weather.py | Weather API client, data fetching, caching |
| services/location.py | Location detection, coordinate management |
| models/weather_data.py | Data classes for weather information |
| utils/config.py | Configuration loading, validation, defaults |
| utils/icons.py | Weather icon mapping and loading |
| assets/ | Weather icons, fonts, and other static resources |

### 7.2 Data Flow

1. Application starts and loads configuration from config.yaml
2. Location service determines coordinates (from config or auto-detect)
3. Weather service fetches initial data from Open-Meteo API
4. GUI initializes in fullscreen landscape mode
5. Time display updates every second via Tkinter after() method
6. Weather service refreshes data on configured interval (default 15 min)
7. Touch events on temperature zone trigger forecast view transition
8. Auto-return timer returns to main view after inactivity

### 7.3 Threading Model

The application uses a single-threaded model with Tkinter's event loop for simplicity and reliability:

- Main thread: GUI rendering and event handling
- Network requests: Use requests library with timeout, scheduled via after()
- Alternative: Background thread for API calls with queue for GUI updates
- All GUI updates must occur on main thread

---

## 8. Data Models

### 8.1 Configuration Schema

Configuration is stored in YAML format at `~/.config/weatherclock/config.yaml`:

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| location.latitude | float | null (auto) | Latitude coordinate |
| location.longitude | float | null (auto) | Longitude coordinate |
| location.name | string | "" | Display name for location |
| display.temperature_unit | string | "fahrenheit" | fahrenheit or celsius |
| display.time_format | string | "12h" | 12h or 24h |
| display.show_seconds | bool | true | Show seconds in time |
| display.theme | string | "dark" | dark or light |
| refresh.weather_interval | int | 900 | Seconds between API calls |
| refresh.forecast_timeout | int | 30 | Seconds before auto-return |

#### Example config.yaml

```yaml
location:
  latitude: 40.7128
  longitude: -74.0060
  name: "New York, NY"

display:
  temperature_unit: "fahrenheit"
  time_format: "12h"
  show_seconds: true
  theme: "dark"

refresh:
  weather_interval: 900
  forecast_timeout: 30
```

### 8.2 Weather Data Structure

Internal data class for current weather:

| Field | Type | Description |
|-------|------|-------------|
| temperature | float | Current temperature |
| feels_like | float | Apparent temperature |
| condition | enum | SUNNY, CLOUDY, RAIN, SNOW |
| weather_code | int | WMO weather code |
| humidity | int | Relative humidity percentage |
| timestamp | datetime | Time of observation |
| is_day | bool | Daytime or nighttime |

#### Python Implementation

```python
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class WeatherCondition(Enum):
    SUNNY = "sunny"
    CLOUDY = "cloudy"
    RAIN = "rain"
    SNOW = "snow"

@dataclass
class CurrentWeather:
    temperature: float
    feels_like: float
    condition: WeatherCondition
    weather_code: int
    humidity: int
    timestamp: datetime
    is_day: bool
```

### 8.3 Forecast Data Structure

Data class for daily forecast:

| Field | Type | Description |
|-------|------|-------------|
| date | date | Forecast date |
| day_name | string | Day of week (e.g., "Monday") |
| high_temp | float | Maximum temperature |
| low_temp | float | Minimum temperature |
| condition | enum | SUNNY, CLOUDY, RAIN, SNOW |
| weather_code | int | WMO weather code |

#### Python Implementation

```python
from dataclasses import dataclass
from datetime import date

@dataclass
class DailyForecast:
    date: date
    day_name: str
    high_temp: float
    low_temp: float
    condition: WeatherCondition
    weather_code: int
```

---

## 9. Implementation Guide

### 9.1 Project Structure

```
weatherclock/
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── config.yaml.example        # Example configuration
├── README.md                  # Documentation
├── gui/
│   ├── __init__.py
│   ├── display.py             # Main display class
│   ├── main_view.py           # Main view implementation
│   ├── forecast_view.py       # Forecast view implementation
│   └── widgets.py             # Custom widgets
├── services/
│   ├── __init__.py
│   ├── weather.py             # Weather API client
│   └── location.py            # Location detection
├── models/
│   ├── __init__.py
│   └── weather_data.py        # Data classes
├── utils/
│   ├── __init__.py
│   ├── config.py              # Configuration management
│   └── icons.py               # Icon utilities
└── assets/
    ├── icons/                 # Weather icons (SVG/PNG)
    └── fonts/                 # Custom fonts (if needed)
```

### 9.2 Key Implementation Details

#### 9.2.1 Fullscreen Landscape Setup

Configure Tkinter window for fullscreen landscape operation:

```python
import tkinter as tk

root = tk.Tk()
root.attributes('-fullscreen', True)
root.config(cursor='none')  # Hide cursor
root.bind('<Escape>', lambda e: root.attributes('-fullscreen', False))  # Dev exit
```

#### 9.2.2 Touch Event Handling

```python
class TemperatureWidget(tk.Frame):
    def __init__(self, parent, on_tap_callback):
        super().__init__(parent)
        self.on_tap = on_tap_callback
        self.last_tap_time = 0
        self.bind('<Button-1>', self._handle_tap)
        
    def _handle_tap(self, event):
        current_time = time.time()
        if current_time - self.last_tap_time > 0.2:  # 200ms debounce
            self.last_tap_time = current_time
            self._show_tap_feedback()
            self.on_tap()
    
    def _show_tap_feedback(self):
        original_bg = self.cget('background')
        self.config(background='#81d4fa')
        self.after(100, lambda: self.config(background=original_bg))
```

#### 9.2.3 Weather API Client

```python
import requests
from typing import Optional, Tuple, List

class WeatherService:
    BASE_URL = "https://api.open-meteo.com/v1/forecast"
    
    def __init__(self, latitude: float, longitude: float, unit: str = "fahrenheit"):
        self.latitude = latitude
        self.longitude = longitude
        self.unit = unit
        self.cache: Optional[dict] = None
        self.cache_time: Optional[datetime] = None
    
    def get_weather(self) -> Tuple[CurrentWeather, List[DailyForecast]]:
        params = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "current": "temperature_2m,apparent_temperature,weather_code,is_day",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min",
            "temperature_unit": self.unit,
            "timezone": "auto",
            "forecast_days": 5
        }
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            self.cache = data
            self.cache_time = datetime.now()
            return self._parse_response(data)
        except requests.RequestException as e:
            if self.cache:
                return self._parse_response(self.cache)
            raise
    
    def _parse_response(self, data: dict) -> Tuple[CurrentWeather, List[DailyForecast]]:
        current = self._parse_current(data["current"])
        forecast = self._parse_forecast(data["daily"])
        return current, forecast
    
    @staticmethod
    def _map_condition(code: int) -> WeatherCondition:
        if code in [0, 1]:
            return WeatherCondition.SUNNY
        elif code in [2, 3, 45, 48]:
            return WeatherCondition.CLOUDY
        elif code in [71, 73, 75, 77, 85, 86]:
            return WeatherCondition.SNOW
        else:
            return WeatherCondition.RAIN
```

#### 9.2.4 Efficient Time Updates

```python
class TimeWidget(tk.Label):
    def __init__(self, parent, time_format: str = "12h", show_seconds: bool = True):
        super().__init__(parent)
        self.time_format = time_format
        self.show_seconds = show_seconds
        self._update_time()
    
    def _update_time(self):
        now = datetime.now()
        
        if self.time_format == "12h":
            if self.show_seconds:
                time_str = now.strftime("%I:%M:%S %p")
            else:
                time_str = now.strftime("%I:%M %p")
        else:
            if self.show_seconds:
                time_str = now.strftime("%H:%M:%S")
            else:
                time_str = now.strftime("%H:%M")
        
        self.config(text=time_str.lstrip('0'))
        
        # Schedule next update
        interval = 1000 if self.show_seconds else 60000
        self.after(interval, self._update_time)
```

### 9.3 Dependencies (requirements.txt)

```
requests>=2.31.0
Pillow>=10.0.0
python-dateutil>=2.8.2
PyYAML>=6.0
```

Note: Tkinter is included with Python on Raspberry Pi OS and does not need to be listed.

---

## 10. Testing Requirements

### 10.1 Unit Tests

| Test Area | Test Cases |
|-----------|------------|
| Weather API Client | Successful response parsing, timeout handling, retry logic, cache behavior |
| Weather Code Mapping | All WMO codes map to correct conditions, edge cases |
| Configuration Loading | Default values, file parsing, validation, missing file handling |
| Date/Time Formatting | 12h/24h formats, date formats, timezone handling |
| Temperature Conversion | Fahrenheit/Celsius display, rounding |

### 10.2 Integration Tests

- End-to-end API call with real Open-Meteo endpoint
- GUI initialization and rendering on target display
- Touch event detection and view transitions
- Auto-return timer functionality

### 10.3 Performance Tests

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Application startup time | < 5 seconds | Time from launch to display |
| Touch response latency | < 100ms | Time from tap to visual feedback |
| Memory usage (idle) | < 100MB | Monitor with htop/free |
| Memory usage (24h) | No growth > 10% | Log memory at intervals |
| CPU usage (idle) | < 5% | Monitor with htop/top |
| API call duration | < 2 seconds | Request timing logs |

### 10.4 Stability Tests

- 72-hour continuous operation test
- Network disconnection and reconnection handling
- API unavailability simulation (firewall blocking)
- Repeated touch interactions (1000+ taps)

---

## 11. Deployment Guide

### 11.1 Raspberry Pi OS Setup

1. Download and flash Raspberry Pi OS (64-bit) to microSD card using Raspberry Pi Imager
2. Boot Raspberry Pi and complete initial setup (WiFi, locale, etc.)
3. Update system: `sudo apt update && sudo apt upgrade -y`
4. Install Python dependencies: `pip3 install -r requirements.txt`
5. Configure display rotation if needed (see Appendix B)

### 11.2 Application Installation

1. Clone or copy application to `/home/pi/weatherclock/`
2. Copy config.yaml.example to `~/.config/weatherclock/config.yaml`
3. Edit configuration with your location and preferences
4. Test run: `python3 /home/pi/weatherclock/main.py`
5. Verify display, touch, and weather data

### 11.3 Auto-Start Configuration

Create a systemd service for automatic startup:

**File:** `/etc/systemd/system/weatherclock.service`

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

Enable the service:

```bash
sudo systemctl enable weatherclock.service
sudo systemctl start weatherclock.service
```

### 11.4 Kiosk Mode Setup

For a dedicated display that only shows the weather app:

1. Disable screen blanking:
   ```bash
   xset s off
   xset -dpms
   xset s noblank
   ```

2. Add to `~/.config/lxsession/LXDE-pi/autostart`:
   ```
   @xset s off
   @xset -dpms
   @xset s noblank
   @python3 /home/pi/weatherclock/main.py
   ```

3. Hide taskbar and desktop icons via Raspberry Pi Configuration

4. Consider using a minimal window manager like Openbox for faster boot

---

## 12. Maintenance & Support

### 12.1 Logging

The application logs to `~/.local/log/weatherclock/app.log` with the following levels:

- **INFO:** Application start/stop, weather updates, view transitions
- **WARNING:** API failures (with retry), network issues, cache usage
- **ERROR:** Unhandled exceptions, critical failures
- **DEBUG:** API responses, configuration loading, touch events (if enabled)

Logs are rotated daily with 7-day retention.

#### Logging Configuration

```python
import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging():
    log_dir = os.path.expanduser("~/.local/log/weatherclock")
    os.makedirs(log_dir, exist_ok=True)
    
    handler = RotatingFileHandler(
        os.path.join(log_dir, "app.log"),
        maxBytes=1_000_000,
        backupCount=7
    )
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[handler]
    )
```

### 12.2 Monitoring

Recommended monitoring for production deployment:

- Memory usage alerts if exceeds 150MB
- Process restart alerts via systemd
- Network connectivity checks
- Disk space monitoring (for logs)

### 12.3 Updates

Application updates can be performed via:

- Git pull (if using version control)
- Manual file replacement
- Restart service after update: `sudo systemctl restart weatherclock`
- Configuration preserved in separate directory (`~/.config/weatherclock/`)

---

## 13. Future Enhancements

### 13.1 Phase 2 Features

- Hourly forecast view (swipe or tap to access)
- Additional weather data: humidity, wind speed, UV index
- Weather alerts and warnings display
- Multiple location support (swipe between locations)
- Light theme option

### 13.2 Phase 3 Features

- Animated weather icons
- Dynamic backgrounds based on weather/time of day
- Calendar integration showing upcoming events
- Alarm/reminder functionality
- Web-based configuration interface
- Voice control integration (wake word + commands)

---

## Appendix A: Open-Meteo API Reference

### A.1 Complete API Endpoint

**Base URL:** `https://api.open-meteo.com/v1/forecast`

Required query parameters for this application:

```
?latitude={lat}
&longitude={lon}
&current=temperature_2m,apparent_temperature,weather_code,is_day
&daily=weather_code,temperature_2m_max,temperature_2m_min
&temperature_unit={unit}
&timezone={tz}
&forecast_days=5
```

### A.2 Response Structure

The API returns JSON with the following structure:

```json
{
  "latitude": 40.710335,
  "longitude": -73.99307,
  "generationtime_ms": 0.058,
  "utc_offset_seconds": -18000,
  "timezone": "America/New_York",
  "timezone_abbreviation": "EST",
  "current_units": {
    "time": "iso8601",
    "temperature_2m": "°F",
    "apparent_temperature": "°F",
    "weather_code": "wmo code",
    "is_day": ""
  },
  "current": {
    "time": "2026-01-17T14:00",
    "temperature_2m": 45.2,
    "apparent_temperature": 38.5,
    "weather_code": 3,
    "is_day": 1
  },
  "daily_units": {
    "time": "iso8601",
    "weather_code": "wmo code",
    "temperature_2m_max": "°F",
    "temperature_2m_min": "°F"
  },
  "daily": {
    "time": ["2026-01-17", "2026-01-18", "2026-01-19", "2026-01-20", "2026-01-21"],
    "weather_code": [3, 61, 3, 71, 0],
    "temperature_2m_max": [48.5, 52.1, 45.0, 38.2, 42.5],
    "temperature_2m_min": [35.2, 38.8, 32.1, 28.5, 30.2]
  }
}
```

### A.3 WMO Weather Codes

| Code | Description |
|------|-------------|
| 0 | Clear sky |
| 1, 2, 3 | Mainly clear, partly cloudy, overcast |
| 45, 48 | Fog, depositing rime fog |
| 51, 53, 55 | Drizzle: light, moderate, dense |
| 56, 57 | Freezing drizzle: light, dense |
| 61, 63, 65 | Rain: slight, moderate, heavy |
| 66, 67 | Freezing rain: light, heavy |
| 71, 73, 75 | Snow fall: slight, moderate, heavy |
| 77 | Snow grains |
| 80, 81, 82 | Rain showers: slight, moderate, violent |
| 85, 86 | Snow showers: slight, heavy |
| 95 | Thunderstorm: slight or moderate |
| 96, 99 | Thunderstorm with hail: slight, heavy |

### A.4 Condition Mapping Code

```python
def map_wmo_to_condition(code: int) -> str:
    """Map WMO weather code to simplified condition."""
    
    SUNNY_CODES = {0, 1}
    CLOUDY_CODES = {2, 3, 45, 48}
    SNOW_CODES = {71, 73, 75, 77, 85, 86}
    # All other codes map to RAIN
    
    if code in SUNNY_CODES:
        return "sunny"
    elif code in CLOUDY_CODES:
        return "cloudy"
    elif code in SNOW_CODES:
        return "snow"
    else:
        return "rain"
```

---

## Appendix B: Hardware Setup

### B.1 Display Rotation

To rotate the display for landscape orientation, edit `/boot/config.txt`:

**For official Raspberry Pi Touch Display:**
```
lcd_rotate=2    # Rotate 180 degrees if needed
```

**For HDMI displays:**
```
display_rotate=1    # 90 degrees
display_rotate=2    # 180 degrees
display_rotate=3    # 270 degrees
```

**For Wayland (Raspberry Pi OS Bookworm and later):**
```bash
# Use wlr-randr or raspi-config
sudo raspi-config
# Navigate to: Display Options > Screen Orientation
```

### B.2 Touchscreen Calibration

If touch input is misaligned, calibrate using:

```bash
sudo apt install xinput-calibrator
DISPLAY=:0 xinput_calibrator
```

Follow on-screen instructions and save calibration data to `/etc/X11/xorg.conf.d/`

### B.3 Recommended Hardware

| Component | Recommendation |
|-----------|----------------|
| Display (Official) | Raspberry Pi Touch Display (7", 800x480) |
| Display (Third-party) | Waveshare 7" IPS (1024x600) or similar |
| Case | SmartiPi Touch 2 or similar display case |
| Power Supply | Official 27W USB-C (required for Pi 5) |
| MicroSD | Samsung EVO Plus 32GB or better |

### B.4 Disable Screen Blanking Permanently

Create `/etc/X11/xorg.conf.d/10-blanking.conf`:

```
Section "ServerFlags"
    Option "BlankTime" "0"
    Option "StandbyTime" "0"
    Option "SuspendTime" "0"
    Option "OffTime" "0"
EndSection
```

---

## Appendix C: Troubleshooting

| Issue | Solution |
|-------|----------|
| Application won't start | Check logs at `~/.local/log/weatherclock/`. Verify Python and dependencies installed. |
| No weather data displayed | Verify internet connection. Check API endpoint accessibility. Review config.yaml for valid coordinates. |
| Touch not responding | Check touchscreen drivers. Run `xinput list` to verify device detected. Re-calibrate if needed. |
| Display is vertical | Edit `/boot/config.txt` to set display_rotate. Reboot required. |
| High CPU usage | Reduce logging level. Check for infinite loops. Monitor with htop. |
| Memory leak suspected | Check for accumulating PhotoImage objects. Ensure proper widget cleanup. |
| Application crashes after hours | Review error logs. Check for memory issues. Verify network stability. |
| Incorrect time displayed | Verify NTP is running: `timedatectl status`. Check timezone in config. |
| Icons not loading | Verify `assets/icons/` directory exists. Check file permissions. Confirm PNG/SVG format. |
| Forecast view not triggering | Verify touch events bound to temperature widget. Check debounce timing. |
| API returns errors | Check rate limits (10K/day). Verify coordinates are valid. Test URL in browser. |

### Common Commands

```bash
# Check service status
sudo systemctl status weatherclock

# View live logs
journalctl -u weatherclock.service -f

# Test API manually
curl "https://api.open-meteo.com/v1/forecast?latitude=40.71&longitude=-74.00&current=temperature_2m&timezone=auto"

# Check network connectivity
ping -c 3 api.open-meteo.com

# Monitor resources
htop

# Check NTP status
timedatectl status

# Restart the application
sudo systemctl restart weatherclock
```

---

## Document Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-17 | Initial release |

---

*End of Document*
