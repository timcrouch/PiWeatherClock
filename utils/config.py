"""
Configuration management for WeatherClock Pi.

Handles loading, validation, and defaults for application configuration.
"""

import os
import yaml
import logging
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path


logger = logging.getLogger(__name__)


@dataclass
class LocationConfig:
    """Location configuration."""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    name: str = ""
    
    def is_configured(self) -> bool:
        """Check if location coordinates are set."""
        return self.latitude is not None and self.longitude is not None


@dataclass
class DisplayConfig:
    """Display configuration."""
    temperature_unit: str = "fahrenheit"
    time_format: str = "12h"
    show_seconds: bool = True
    theme: str = "dark"
    
    def __post_init__(self):
        """Validate configuration values."""
        if self.temperature_unit not in ("fahrenheit", "celsius"):
            logger.warning(f"Invalid temperature_unit '{self.temperature_unit}', using 'fahrenheit'")
            self.temperature_unit = "fahrenheit"
        
        if self.time_format not in ("12h", "24h"):
            logger.warning(f"Invalid time_format '{self.time_format}', using '12h'")
            self.time_format = "12h"
        
        if self.theme not in ("dark", "light"):
            logger.warning(f"Invalid theme '{self.theme}', using 'dark'")
            self.theme = "dark"


@dataclass
class RefreshConfig:
    """Refresh timing configuration."""
    weather_interval: int = 900  # 15 minutes
    forecast_timeout: int = 30   # seconds before auto-return
    
    def __post_init__(self):
        """Validate and constrain configuration values."""
        # Minimum 5 minutes between API calls
        if self.weather_interval < 300:
            logger.warning(f"weather_interval {self.weather_interval} too low, using 300")
            self.weather_interval = 300
        
        # Reasonable timeout range
        if self.forecast_timeout < 5:
            self.forecast_timeout = 5
        elif self.forecast_timeout > 300:
            self.forecast_timeout = 300


@dataclass
class ThemeColors:
    """Color scheme for the application."""
    background: str = "#1a1a2e"
    primary_text: str = "#ffffff"
    secondary_text: str = "#b0b0b0"
    accent: str = "#4fc3f7"
    touch_highlight: str = "#81d4fa"
    warning: str = "#ff9800"
    error: str = "#f44336"


@dataclass 
class AppConfig:
    """Main application configuration."""
    location: LocationConfig = field(default_factory=LocationConfig)
    display: DisplayConfig = field(default_factory=DisplayConfig)
    refresh: RefreshConfig = field(default_factory=RefreshConfig)
    
    def get_theme_colors(self) -> ThemeColors:
        """Get color scheme based on theme setting."""
        if self.display.theme == "light":
            return ThemeColors(
                background="#f5f5f5",
                primary_text="#212121",
                secondary_text="#757575",
                accent="#1976d2",
                touch_highlight="#64b5f6",
                warning="#f57c00",
                error="#d32f2f"
            )
        return ThemeColors()  # Default dark theme


def get_config_path() -> Path:
    """Get the configuration file path."""
    # Use XDG config directory
    config_home = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
    return Path(config_home) / "weatherclock" / "config.yaml"


def load_config(config_path: Optional[Path] = None) -> AppConfig:
    """
    Load configuration from YAML file.
    
    Falls back to defaults if file doesn't exist or has errors.
    """
    if config_path is None:
        config_path = get_config_path()
    
    config = AppConfig()
    
    if not config_path.exists():
        logger.info(f"No config file found at {config_path}, using defaults")
        return config
    
    try:
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)
        
        if data is None:
            logger.warning("Config file is empty, using defaults")
            return config
        
        # Parse location
        if "location" in data and data["location"]:
            loc = data["location"]
            config.location = LocationConfig(
                latitude=loc.get("latitude"),
                longitude=loc.get("longitude"),
                name=loc.get("name", "")
            )
        
        # Parse display
        if "display" in data and data["display"]:
            disp = data["display"]
            config.display = DisplayConfig(
                temperature_unit=disp.get("temperature_unit", "fahrenheit"),
                time_format=disp.get("time_format", "12h"),
                show_seconds=disp.get("show_seconds", True),
                theme=disp.get("theme", "dark")
            )
        
        # Parse refresh
        if "refresh" in data and data["refresh"]:
            ref = data["refresh"]
            config.refresh = RefreshConfig(
                weather_interval=ref.get("weather_interval", 900),
                forecast_timeout=ref.get("forecast_timeout", 30)
            )
        
        logger.info(f"Configuration loaded from {config_path}")
        return config
        
    except yaml.YAMLError as e:
        logger.error(f"Error parsing config file: {e}")
        return AppConfig()
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return AppConfig()


def save_config(config: AppConfig, config_path: Optional[Path] = None) -> bool:
    """Save configuration to YAML file."""
    if config_path is None:
        config_path = get_config_path()
    
    try:
        # Ensure directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "location": {
                "latitude": config.location.latitude,
                "longitude": config.location.longitude,
                "name": config.location.name
            },
            "display": {
                "temperature_unit": config.display.temperature_unit,
                "time_format": config.display.time_format,
                "show_seconds": config.display.show_seconds,
                "theme": config.display.theme
            },
            "refresh": {
                "weather_interval": config.refresh.weather_interval,
                "forecast_timeout": config.refresh.forecast_timeout
            }
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
        
        logger.info(f"Configuration saved to {config_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving config: {e}")
        return False
