"""
Custom widgets for WeatherClock Pi.

Contains reusable UI components for the weather clock display.
"""

import tkinter as tk
from tkinter import font as tkfont
from datetime import datetime
from typing import Callable, Optional
import logging

from models.weather_data import WeatherCondition, CurrentWeather, DailyForecast
from utils.config import ThemeColors
from utils.icons import get_icon_manager


logger = logging.getLogger(__name__)


class TimeWidget(tk.Frame):
    """Widget displaying the current time with auto-update."""
    
    def __init__(self, parent, colors: ThemeColors, 
                 time_format: str = "12h", show_seconds: bool = True,
                 **kwargs):
        super().__init__(parent, bg=colors.background, **kwargs)
        
        self.colors = colors
        self.time_format = time_format
        self.show_seconds = show_seconds
        
        # Create time label
        self.time_label = tk.Label(
            self,
            bg=colors.background,
            fg=colors.primary_text,
            font=("Roboto", 96, "bold")
        )
        self.time_label.pack()
        
        # Start updates
        self._update_time()
    
    def _update_time(self):
        """Update the time display."""
        now = datetime.now()
        
        if self.time_format == "12h":
            if self.show_seconds:
                time_str = now.strftime("%I:%M:%S %p")
            else:
                time_str = now.strftime("%I:%M %p")
        else:  # 24h format
            if self.show_seconds:
                time_str = now.strftime("%H:%M:%S")
            else:
                time_str = now.strftime("%H:%M")
        
        # Remove leading zero from hour
        time_str = time_str.lstrip('0')
        
        self.time_label.config(text=time_str)
        
        # Schedule next update
        interval = 1000 if self.show_seconds else 60000
        self.after(interval, self._update_time)
    
    def set_font_size(self, size: int):
        """Update the font size."""
        self.time_label.config(font=("Roboto", size, "bold"))


class DateWidget(tk.Label):
    """Widget displaying the current date."""
    
    def __init__(self, parent, colors: ThemeColors, **kwargs):
        super().__init__(
            parent,
            bg=colors.background,
            fg=colors.secondary_text,
            font=("Roboto", 28),
            **kwargs
        )
        
        self._update_date()
    
    def _update_date(self):
        """Update the date display."""
        now = datetime.now()
        date_str = now.strftime("%A, %B %d, %Y")
        self.config(text=date_str)
        
        # Calculate time until midnight for next update
        tomorrow = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        from datetime import timedelta
        tomorrow = tomorrow + timedelta(days=1)
        ms_until_midnight = int((tomorrow - datetime.now()).total_seconds() * 1000)
        
        # Update at midnight (or every hour as fallback)
        update_interval = min(ms_until_midnight, 3600000)
        self.after(update_interval, self._update_date)


class TemperatureWidget(tk.Frame):
    """
    Widget displaying temperature with touch support.
    
    Tapping this widget triggers the forecast view.
    """
    
    def __init__(self, parent, colors: ThemeColors, 
                 on_tap: Optional[Callable] = None,
                 unit: str = "fahrenheit",
                 **kwargs):
        super().__init__(parent, bg=colors.background, **kwargs)
        
        self.colors = colors
        self.on_tap = on_tap
        self.unit = unit
        self.last_tap_time = 0
        
        # Create container with visual indicator for touchability
        self.container = tk.Frame(
            self,
            bg=colors.background,
            highlightbackground=colors.accent,
            highlightthickness=2,
            padx=15,
            pady=10
        )
        self.container.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
        
        # Current temperature label
        self.temp_label = tk.Label(
            self.container,
            text="--°",
            bg=colors.background,
            fg=colors.primary_text,
            font=("Roboto", 72, "bold")
        )
        self.temp_label.pack()
        
        # Feels like label
        self.feels_like_label = tk.Label(
            self.container,
            text="Feels like --°",
            bg=colors.background,
            fg=colors.secondary_text,
            font=("Roboto", 18)
        )
        self.feels_like_label.pack()
        
        # Tap hint
        self.hint_label = tk.Label(
            self.container,
            text="Tap for forecast",
            bg=colors.background,
            fg=colors.accent,
            font=("Roboto", 12)
        )
        self.hint_label.pack(pady=(10, 0))
        
        # Bind touch/click events
        for widget in [self, self.container, self.temp_label, 
                       self.feels_like_label, self.hint_label]:
            widget.bind('<Button-1>', self._handle_tap)
    
    def _handle_tap(self, event):
        """Handle tap with debounce."""
        import time
        current_time = time.time()
        
        # 200ms debounce
        if current_time - self.last_tap_time > 0.2:
            self.last_tap_time = current_time
            self._show_tap_feedback()
            
            if self.on_tap:
                self.on_tap()
    
    def _show_tap_feedback(self):
        """Show visual feedback on tap."""
        original_bg = self.container.cget('highlightbackground')
        self.container.config(highlightbackground=self.colors.touch_highlight)
        self.after(100, lambda: self.container.config(highlightbackground=original_bg))
    
    def update_weather(self, weather: CurrentWeather):
        """Update the displayed temperature."""
        symbol = "°F" if self.unit == "fahrenheit" else "°C"
        
        self.temp_label.config(text=f"{weather.temperature:.0f}{symbol}")
        self.feels_like_label.config(text=f"Feels like {weather.feels_like:.0f}{symbol}")


class WeatherIconWidget(tk.Frame):
    """Widget displaying weather icon and condition text."""
    
    def __init__(self, parent, colors: ThemeColors, icon_size: int = 128, **kwargs):
        super().__init__(parent, bg=colors.background, **kwargs)
        
        self.colors = colors
        self.icon_size = icon_size
        self.icon_manager = get_icon_manager()
        self._current_photo = None  # Keep reference to prevent garbage collection
        
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
            font=("Roboto", 28, "bold")
        )
        self.condition_label.pack()
        
        # Location name
        self.location_label = tk.Label(
            self,
            text="",
            bg=colors.background,
            fg=colors.secondary_text,
            font=("Roboto", 14)
        )
        self.location_label.pack(pady=(5, 0))
    
    def update_weather(self, weather: CurrentWeather, location_name: str = ""):
        """Update the weather icon and condition."""
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
            self._current_photo = photo  # Keep reference
            self.icon_label.config(image=photo)
        else:
            # Fallback to text if icon not available
            self.icon_label.config(text="🌤", font=("Roboto", 64))


class ForecastDayWidget(tk.Frame):
    """Widget displaying a single day's forecast."""
    
    def __init__(self, parent, colors: ThemeColors, 
                 is_today: bool = False, icon_size: int = 64, **kwargs):
        super().__init__(parent, bg=colors.background, **kwargs)
        
        self.colors = colors
        self.icon_size = icon_size
        self.icon_manager = get_icon_manager()
        self._current_photo = None
        
        # Highlight today
        if is_today:
            self.config(
                highlightbackground=colors.accent,
                highlightthickness=2,
                padx=10,
                pady=10
            )
        
        # Day name
        self.day_label = tk.Label(
            self,
            text="--",
            bg=colors.background,
            fg=colors.primary_text,
            font=("Roboto", 18, "bold")
        )
        self.day_label.pack(pady=(5, 10))
        
        # Weather icon
        self.icon_label = tk.Label(
            self,
            bg=colors.background
        )
        self.icon_label.pack(pady=5)
        
        # High temperature
        self.high_label = tk.Label(
            self,
            text="--°",
            bg=colors.background,
            fg=colors.primary_text,
            font=("Roboto", 22)
        )
        self.high_label.pack()
        
        # Low temperature
        self.low_label = tk.Label(
            self,
            text="--°",
            bg=colors.background,
            fg=colors.secondary_text,
            font=("Roboto", 18)
        )
        self.low_label.pack()
    
    def update_forecast(self, forecast: DailyForecast, unit: str = "fahrenheit"):
        """Update the forecast display."""
        # Day name (use "Today" for today)
        if forecast.is_today():
            self.day_label.config(text="Today")
        else:
            # Short day name
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
            self.icon_label.config(text="☁", font=("Roboto", 32))


class StatusWidget(tk.Label):
    """Widget showing status messages (offline, last updated, etc.)."""
    
    def __init__(self, parent, colors: ThemeColors, **kwargs):
        super().__init__(
            parent,
            text="",
            bg=colors.background,
            fg=colors.secondary_text,
            font=("Roboto", 10),
            **kwargs
        )
        
        self.colors = colors
    
    def show_offline(self):
        """Show offline indicator."""
        self.config(text="⚠ Offline - Using cached data", fg=self.colors.warning)
    
    def show_updating(self):
        """Show updating indicator."""
        self.config(text="Updating...", fg=self.colors.secondary_text)
    
    def show_last_updated(self, timestamp: datetime):
        """Show last updated time."""
        time_str = timestamp.strftime("%I:%M %p").lstrip('0')
        self.config(text=f"Updated {time_str}", fg=self.colors.secondary_text)
    
    def clear(self):
        """Clear the status."""
        self.config(text="")
