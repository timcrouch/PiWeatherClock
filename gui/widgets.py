"""
Custom widgets for WeatherClock Pi.

Contains reusable UI components for the weather clock display.
Redesigned for multi-timezone layout with cards.
"""

import tkinter as tk
from datetime import datetime
from typing import Callable, Optional
import logging
try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

from models.weather_data import WeatherCondition, CurrentWeather, DailyForecast
from utils.config import ThemeColors, TimezoneConfig
from utils.icons import get_icon_manager


logger = logging.getLogger(__name__)


class MainClockWidget(tk.Frame):
    """
    Main clock widget with large time display.
    Shows time, location, and date for the primary timezone.
    """
    
    def __init__(self, parent, colors: ThemeColors,
                 timezone_config: TimezoneConfig,
                 time_format: str = "12h",
                 show_seconds: bool = True,
                 **kwargs):
        super().__init__(parent, bg=colors.background, **kwargs)
        
        self.colors = colors
        self.timezone_config = timezone_config
        self.time_format = time_format
        self.show_seconds = show_seconds
        
        try:
            self.tz = ZoneInfo(timezone_config.timezone)
        except Exception:
            self.tz = None
            logger.warning(f"Invalid timezone: {timezone_config.timezone}")
        
        # Time display (large)
        self.time_label = tk.Label(
            self,
            bg=colors.background,
            fg=colors.primary_text,
            font=("Helvetica", 72, "bold")
        )
        self.time_label.pack(anchor="w")
        
        # Location label (accent color)
        self.location_label = tk.Label(
            self,
            text=timezone_config.get_display_label(),
            bg=colors.background,
            fg=colors.accent,
            font=("Helvetica", 20)
        )
        self.location_label.pack(anchor="w", pady=(5, 0))
        
        # Date label
        self.date_label = tk.Label(
            self,
            bg=colors.background,
            fg=colors.secondary_text,
            font=("Helvetica", 16)
        )
        self.date_label.pack(anchor="w", pady=(2, 0))
        
        # Start updates
        self._update_time()
    
    def _update_time(self):
        """Update the time display."""
        if self.tz:
            now = datetime.now(self.tz)
        else:
            now = datetime.now()
        
        # Format time
        if self.time_format == "12h":
            if self.show_seconds:
                time_str = now.strftime("%I:%M:%S")
                ampm = now.strftime("%p")
            else:
                time_str = now.strftime("%I:%M")
                ampm = now.strftime("%p")
            # Remove leading zero
            time_str = time_str.lstrip('0')
            self.time_label.config(text=f"{time_str} {ampm}")
        else:
            if self.show_seconds:
                time_str = now.strftime("%H:%M:%S")
            else:
                time_str = now.strftime("%H:%M")
            self.time_label.config(text=time_str)
        
        # Format date
        date_str = now.strftime("%A, %B %d, %Y")
        self.date_label.config(text=date_str)
        
        # Schedule next update
        interval = 1000 if self.show_seconds else 60000
        self.after(interval, self._update_time)
    
    def update_timezone(self, timezone_config: TimezoneConfig):
        """Update the timezone configuration."""
        self.timezone_config = timezone_config
        try:
            self.tz = ZoneInfo(timezone_config.timezone)
        except Exception:
            self.tz = None
        self.location_label.config(text=timezone_config.get_display_label())


class SecondaryClockWidget(tk.Frame):
    """
    Secondary clock widget in a card style.
    Shows time and location for additional timezones.
    """
    
    def __init__(self, parent, colors: ThemeColors,
                 timezone_config: TimezoneConfig,
                 time_format: str = "12h",
                 **kwargs):
        super().__init__(parent, bg=colors.card_background, 
                        highlightbackground=colors.divider,
                        highlightthickness=1,
                        padx=15, pady=10, **kwargs)
        
        self.colors = colors
        self.timezone_config = timezone_config
        self.time_format = time_format
        
        try:
            self.tz = ZoneInfo(timezone_config.timezone)
        except Exception:
            self.tz = None
            logger.warning(f"Invalid timezone: {timezone_config.timezone}")
        
        # Time display
        self.time_label = tk.Label(
            self,
            bg=colors.card_background,
            fg=colors.primary_text,
            font=("Helvetica", 24, "bold")
        )
        self.time_label.pack()
        
        # Location label (accent color)
        self.location_label = tk.Label(
            self,
            text=timezone_config.label,
            bg=colors.card_background,
            fg=colors.accent,
            font=("Helvetica", 12)
        )
        self.location_label.pack(pady=(2, 0))
        
        # Country label
        self.country_label = tk.Label(
            self,
            text=timezone_config.country,
            bg=colors.card_background,
            fg=colors.secondary_text,
            font=("Helvetica", 10)
        )
        self.country_label.pack()
        
        # Start updates
        self._update_time()
    
    def _update_time(self):
        """Update the time display."""
        if self.tz:
            now = datetime.now(self.tz)
        else:
            now = datetime.now()
        
        # Format time (no seconds for secondary clocks)
        if self.time_format == "12h":
            time_str = now.strftime("%I:%M")
            ampm = now.strftime("%p")
            time_str = time_str.lstrip('0')
            self.time_label.config(text=f"{time_str} {ampm}")
        else:
            time_str = now.strftime("%H:%M")
            self.time_label.config(text=time_str)
        
        # Update every minute
        self.after(60000, self._update_time)
    
    def update_timezone(self, timezone_config: TimezoneConfig):
        """Update the timezone configuration."""
        self.timezone_config = timezone_config
        try:
            self.tz = ZoneInfo(timezone_config.timezone)
        except Exception:
            self.tz = None
        self.location_label.config(text=timezone_config.label)
        self.country_label.config(text=timezone_config.country)


class WeatherCardWidget(tk.Frame):
    """
    Weather card showing icon, condition, and location.
    """
    
    def __init__(self, parent, colors: ThemeColors, icon_size: int = 80, **kwargs):
        super().__init__(parent, bg=colors.background, **kwargs)
        
        self.colors = colors
        self.icon_size = icon_size
        self.icon_manager = get_icon_manager()
        self._current_photo = None
        
        # Icon label
        self.icon_label = tk.Label(
            self,
            bg=colors.background
        )
        self.icon_label.pack(pady=(0, 10))
        
        # Condition text
        self.condition_label = tk.Label(
            self,
            text="--",
            bg=colors.background,
            fg=colors.primary_text,
            font=("Helvetica", 24, "bold")
        )
        self.condition_label.pack()
        
        # Location with pin icon
        self.location_frame = tk.Frame(self, bg=colors.background)
        self.location_frame.pack(pady=(8, 0))
        
        self.pin_label = tk.Label(
            self.location_frame,
            text="📍",
            bg=colors.background,
            fg=colors.secondary_text,
            font=("Helvetica", 12)
        )
        self.pin_label.pack(side=tk.LEFT)
        
        self.location_label = tk.Label(
            self.location_frame,
            text="",
            bg=colors.background,
            fg=colors.secondary_text,
            font=("Helvetica", 12)
        )
        self.location_label.pack(side=tk.LEFT)
    
    def update_weather(self, weather: CurrentWeather, location_name: str = ""):
        """Update the weather display."""
        # Update condition text
        self.condition_label.config(text=weather.condition.get_display_text())
        
        # Update location
        if location_name:
            self.location_label.config(text=location_name)
        
        # Load and display icon
        photo = self.icon_manager.load_icon(
            weather.condition, 
            weather.is_day, 
            self.icon_size
        )
        
        if photo:
            self._current_photo = photo
            self.icon_label.config(image=photo)
        else:
            # Fallback to emoji
            emoji_map = {
                WeatherCondition.SUNNY: "☀️" if weather.is_day else "🌙",
                WeatherCondition.CLOUDY: "☁️",
                WeatherCondition.RAIN: "🌧️",
                WeatherCondition.SNOW: "❄️",
            }
            self.icon_label.config(
                text=emoji_map.get(weather.condition, "☁️"),
                font=("Helvetica", 48)
            )


class TemperatureCardWidget(tk.Frame):
    """
    Temperature card with rounded corners effect.
    Tappable to show forecast.
    """
    
    def __init__(self, parent, colors: ThemeColors,
                 unit: str = "fahrenheit",
                 on_tap: Optional[Callable] = None,
                 **kwargs):
        super().__init__(parent, bg=colors.card_background,
                        highlightbackground=colors.divider,
                        highlightthickness=1,
                        padx=20, pady=15, **kwargs)
        
        self.colors = colors
        self.unit = unit
        self.on_tap = on_tap
        self.last_tap_time = 0
        
        # Header with thermometer icon
        self.header_frame = tk.Frame(self, bg=colors.card_background)
        self.header_frame.pack(anchor="w")
        
        self.thermo_label = tk.Label(
            self.header_frame,
            text="🌡",
            bg=colors.card_background,
            fg=colors.accent,
            font=("Helvetica", 14)
        )
        self.thermo_label.pack(side=tk.LEFT)
        
        self.header_label = tk.Label(
            self.header_frame,
            text="TEMPERATURE",
            bg=colors.card_background,
            fg=colors.accent,
            font=("Helvetica", 12, "bold")
        )
        self.header_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Temperature display
        self.temp_label = tk.Label(
            self,
            text="--°",
            bg=colors.card_background,
            fg=colors.primary_text,
            font=("Helvetica", 48, "bold")
        )
        self.temp_label.pack(pady=(10, 5))
        
        # Feels like
        self.feels_like_label = tk.Label(
            self,
            text="Feels like --°",
            bg=colors.card_background,
            fg=colors.secondary_text,
            font=("Helvetica", 14)
        )
        self.feels_like_label.pack()
        
        # Tap hint
        self.hint_label = tk.Label(
            self,
            text="Tap for 5-day forecast",
            bg=colors.card_background,
            fg=colors.accent,
            font=("Helvetica", 11)
        )
        self.hint_label.pack(pady=(12, 0))
        
        # Bind touch/click events
        for widget in [self, self.header_frame, self.thermo_label, 
                       self.header_label, self.temp_label, 
                       self.feels_like_label, self.hint_label]:
            widget.bind('<Button-1>', self._handle_tap)
    
    def _handle_tap(self, event):
        """Handle tap with debounce."""
        import time
        current_time = time.time()
        
        if current_time - self.last_tap_time > 0.2:
            self.last_tap_time = current_time
            self._show_tap_feedback()
            
            if self.on_tap:
                self.on_tap()
    
    def _show_tap_feedback(self):
        """Show visual feedback on tap."""
        original_bg = self.cget('highlightbackground')
        self.config(highlightbackground=self.colors.accent)
        self.after(100, lambda: self.config(highlightbackground=original_bg))
    
    def update_weather(self, weather: CurrentWeather):
        """Update the temperature display."""
        symbol = "°F" if self.unit == "fahrenheit" else "°C"
        
        self.temp_label.config(text=f"{weather.temperature:.0f}{symbol}")
        self.feels_like_label.config(text=f"Feels like {weather.feels_like:.0f}{symbol}")


class SettingsButton(tk.Label):
    """Settings gear button."""
    
    def __init__(self, parent, colors: ThemeColors,
                 on_click: Optional[Callable] = None,
                 **kwargs):
        super().__init__(
            parent,
            text="⚙️",
            bg=colors.background,
            fg=colors.secondary_text,
            font=("Helvetica", 20),
            cursor="hand2",
            **kwargs
        )
        
        self.colors = colors
        self.on_click = on_click
        
        self.bind('<Button-1>', self._handle_click)
        self.bind('<Enter>', lambda e: self.config(fg=colors.accent))
        self.bind('<Leave>', lambda e: self.config(fg=colors.secondary_text))
    
    def _handle_click(self, event):
        if self.on_click:
            self.on_click()


class StatusWidget(tk.Label):
    """Widget showing status messages (last updated, offline, etc.)."""
    
    def __init__(self, parent, colors: ThemeColors, **kwargs):
        super().__init__(
            parent,
            text="",
            bg=colors.background,
            fg=colors.secondary_text,
            font=("Helvetica", 10),
            **kwargs
        )
        
        self.colors = colors
    
    def show_offline(self):
        """Show offline indicator."""
        self.config(text="⚠️ Offline - Using cached data", fg=self.colors.warning)
    
    def show_updating(self):
        """Show updating indicator."""
        self.config(text="Updating...", fg=self.colors.secondary_text)
    
    def show_last_updated(self, timestamp: datetime):
        """Show last updated time."""
        time_str = timestamp.strftime("%I:%M:%S %p").lstrip('0')
        self.config(text=f"Updated {time_str}", fg=self.colors.secondary_text)
    
    def clear(self):
        """Clear the status."""
        self.config(text="")


class ForecastDayWidget(tk.Frame):
    """Widget displaying a single day's forecast."""
    
    def __init__(self, parent, colors: ThemeColors, 
                 is_today: bool = False, icon_size: int = 48, **kwargs):
        super().__init__(parent, bg=colors.card_background,
                        highlightbackground=colors.accent if is_today else colors.divider,
                        highlightthickness=2 if is_today else 1,
                        padx=10, pady=10, **kwargs)
        
        self.colors = colors
        self.icon_size = icon_size
        self.icon_manager = get_icon_manager()
        self._current_photo = None
        
        # Day name
        self.day_label = tk.Label(
            self,
            text="--",
            bg=colors.card_background,
            fg=colors.primary_text,
            font=("Helvetica", 14, "bold")
        )
        self.day_label.pack(pady=(5, 8))
        
        # Weather icon
        self.icon_label = tk.Label(
            self,
            bg=colors.card_background
        )
        self.icon_label.pack(pady=5)
        
        # High temperature
        self.high_label = tk.Label(
            self,
            text="--°",
            bg=colors.card_background,
            fg=colors.primary_text,
            font=("Helvetica", 18)
        )
        self.high_label.pack()
        
        # Low temperature
        self.low_label = tk.Label(
            self,
            text="--°",
            bg=colors.card_background,
            fg=colors.secondary_text,
            font=("Helvetica", 14)
        )
        self.low_label.pack()
    
    def update_forecast(self, forecast: DailyForecast, unit: str = "fahrenheit"):
        """Update the forecast display."""
        # Day name
        if forecast.is_today():
            self.day_label.config(text="Today")
        else:
            self.day_label.config(text=forecast.day_name[:3])
        
        # Temperatures
        symbol = "°F" if unit == "fahrenheit" else "°C"
        self.high_label.config(text=f"{forecast.high_temp:.0f}{symbol}")
        self.low_label.config(text=f"{forecast.low_temp:.0f}{symbol}")
        
        # Icon
        photo = self.icon_manager.load_icon(forecast.condition, True, self.icon_size)
        
        if photo:
            self._current_photo = photo
            self.icon_label.config(image=photo)
        else:
            emoji_map = {
                WeatherCondition.SUNNY: "☀️",
                WeatherCondition.CLOUDY: "☁️",
                WeatherCondition.RAIN: "🌧️",
                WeatherCondition.SNOW: "❄️",
            }
            self.icon_label.config(
                text=emoji_map.get(forecast.condition, "☁️"),
                font=("Helvetica", 24)
            )
