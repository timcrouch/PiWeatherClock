"""
Main view for WeatherClock Pi.

Displays time, date, current weather, and temperature.
"""

import tkinter as tk
import logging
from typing import Callable, Optional

from models.weather_data import WeatherData
from utils.config import ThemeColors
from gui.widgets import (
    TimeWidget,
    DateWidget,
    TemperatureWidget,
    WeatherIconWidget,
    StatusWidget
)


logger = logging.getLogger(__name__)


class MainView(tk.Frame):
    """
    Main display view with time, weather, and temperature.
    
    Layout:
    - Left (45%): Time and date
    - Center (30%): Weather icon and condition
    - Right (25%): Temperature (tappable for forecast)
    """
    
    def __init__(self, parent, colors: ThemeColors,
                 time_format: str = "12h",
                 show_seconds: bool = True,
                 temperature_unit: str = "fahrenheit",
                 on_temp_tap: Optional[Callable] = None,
                 **kwargs):
        super().__init__(parent, bg=colors.background, **kwargs)
        
        self.colors = colors
        self.temperature_unit = temperature_unit
        self.on_temp_tap = on_temp_tap
        
        # Configure grid weights for responsive layout
        self.grid_columnconfigure(0, weight=45)  # Time zone
        self.grid_columnconfigure(1, weight=30)  # Weather zone
        self.grid_columnconfigure(2, weight=25)  # Temperature zone
        self.grid_rowconfigure(0, weight=1)
        
        # Create zones
        self._create_time_zone(time_format, show_seconds)
        self._create_weather_zone()
        self._create_temperature_zone()
    
    def _create_time_zone(self, time_format: str, show_seconds: bool):
        """Create the time and date display zone."""
        time_frame = tk.Frame(self, bg=self.colors.background)
        time_frame.grid(row=0, column=0, sticky="nsew", padx=20)
        
        # Center the content vertically
        time_frame.grid_rowconfigure(0, weight=1)
        time_frame.grid_rowconfigure(3, weight=1)
        
        # Time widget
        self.time_widget = TimeWidget(
            time_frame,
            self.colors,
            time_format=time_format,
            show_seconds=show_seconds
        )
        self.time_widget.grid(row=1, column=0, sticky="w")
        
        # Date widget
        self.date_widget = DateWidget(time_frame, self.colors)
        self.date_widget.grid(row=2, column=0, sticky="w", pady=(10, 0))
    
    def _create_weather_zone(self):
        """Create the weather icon and condition zone."""
        weather_frame = tk.Frame(self, bg=self.colors.background)
        weather_frame.grid(row=0, column=1, sticky="nsew", padx=10)
        
        # Center content
        weather_frame.grid_rowconfigure(0, weight=1)
        weather_frame.grid_rowconfigure(2, weight=1)
        weather_frame.grid_columnconfigure(0, weight=1)
        
        # Weather icon widget
        self.weather_icon_widget = WeatherIconWidget(
            weather_frame,
            self.colors,
            icon_size=128
        )
        self.weather_icon_widget.grid(row=1, column=0)
        
        # Status widget (for last updated, offline, etc.)
        self.status_widget = StatusWidget(weather_frame, self.colors)
        self.status_widget.grid(row=2, column=0, sticky="s", pady=(0, 20))
    
    def _create_temperature_zone(self):
        """Create the temperature display zone."""
        temp_frame = tk.Frame(self, bg=self.colors.background)
        temp_frame.grid(row=0, column=2, sticky="nsew", padx=20)
        
        # Center content
        temp_frame.grid_rowconfigure(0, weight=1)
        temp_frame.grid_rowconfigure(2, weight=1)
        temp_frame.grid_columnconfigure(0, weight=1)
        
        # Temperature widget with tap handler
        self.temp_widget = TemperatureWidget(
            temp_frame,
            self.colors,
            on_tap=self.on_temp_tap,
            unit=self.temperature_unit
        )
        self.temp_widget.grid(row=1, column=0)
    
    def update_weather(self, weather_data: WeatherData):
        """Update all weather displays with new data."""
        logger.debug("Updating main view with new weather data")
        
        # Update temperature
        self.temp_widget.update_weather(weather_data.current)
        
        # Update weather icon
        self.weather_icon_widget.update_weather(
            weather_data.current,
            weather_data.location_name
        )
        
        # Update status
        self.status_widget.show_last_updated(weather_data.last_updated)
    
    def show_offline_status(self):
        """Show offline indicator."""
        self.status_widget.show_offline()
    
    def show_updating_status(self):
        """Show updating indicator."""
        self.status_widget.show_updating()
