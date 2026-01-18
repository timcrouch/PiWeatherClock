"""
Main view for WeatherClock Pi.

Redesigned layout with:
- Top: Main clock (left) + 2 secondary timezone clocks (right)
- Bottom: Weather card (left) + Temperature card (right)
- Settings gear in top-right corner
"""

import tkinter as tk
import logging
from typing import Callable, Optional

from models.weather_data import WeatherData
from utils.config import ThemeColors, TimezoneConfig
from gui.widgets import (
    MainClockWidget,
    SecondaryClockWidget,
    WeatherCardWidget,
    TemperatureCardWidget,
    SettingsButton,
    StatusWidget
)


logger = logging.getLogger(__name__)


class MainView(tk.Frame):
    """
    Main display view with multi-timezone clocks and weather.
    
    Layout:
    ┌─────────────────────────────────────────────────────────────────┐
    │                                                            ⚙️  │
    ├────────────────────────────────────────┬───────────────────────┤
    │  07:46:10 AM                           │  [Secondary Clock 1]  │
    │  New York, USA                         │  [Secondary Clock 2]  │
    │  Sunday, January 18, 2026              │                       │
    ├────────────────────────────────────────┴───────────────────────┤
    │                           • • •                                 │
    ├────────────────────────────────────────┬───────────────────────┤
    │       [Weather Card]                   │  [Temperature Card]   │
    ├────────────────────────────────────────┴───────────────────────┤
    │ Updated 2:45:52 PM                                              │
    └─────────────────────────────────────────────────────────────────┘
    """
    
    def __init__(self, parent, colors: ThemeColors,
                 main_timezone: TimezoneConfig,
                 secondary_timezone_1: TimezoneConfig,
                 secondary_timezone_2: TimezoneConfig,
                 time_format: str = "12h",
                 show_seconds: bool = True,
                 temperature_unit: str = "fahrenheit",
                 on_temp_tap: Optional[Callable] = None,
                 on_settings_tap: Optional[Callable] = None,
                 **kwargs):
        super().__init__(parent, bg=colors.background, **kwargs)
        
        self.colors = colors
        self.temperature_unit = temperature_unit
        self.on_temp_tap = on_temp_tap
        self.on_settings_tap = on_settings_tap
        
        # Configure main grid
        self.grid_rowconfigure(0, weight=0)   # Settings row
        self.grid_rowconfigure(1, weight=3)   # Clock section
        self.grid_rowconfigure(2, weight=0)   # Divider
        self.grid_rowconfigure(3, weight=2)   # Weather section
        self.grid_rowconfigure(4, weight=0)   # Status row
        self.grid_columnconfigure(0, weight=1)
        
        # Create sections
        self._create_settings_row()
        self._create_clock_section(main_timezone, secondary_timezone_1, 
                                   secondary_timezone_2, time_format, show_seconds)
        self._create_divider()
        self._create_weather_section()
        self._create_status_row()
    
    def _create_settings_row(self):
        """Create the top row with settings gear."""
        settings_frame = tk.Frame(self, bg=self.colors.background)
        settings_frame.grid(row=0, column=0, sticky="ne", padx=15, pady=10)
        
        self.settings_button = SettingsButton(
            settings_frame,
            self.colors,
            on_click=self.on_settings_tap
        )
        self.settings_button.pack()
    
    def _create_clock_section(self, main_tz: TimezoneConfig,
                              sec_tz_1: TimezoneConfig,
                              sec_tz_2: TimezoneConfig,
                              time_format: str,
                              show_seconds: bool):
        """Create the clock section with main and secondary clocks."""
        clock_frame = tk.Frame(self, bg=self.colors.background)
        clock_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        
        # Configure columns
        clock_frame.grid_columnconfigure(0, weight=3)  # Main clock
        clock_frame.grid_columnconfigure(1, weight=1)  # Secondary clocks
        clock_frame.grid_rowconfigure(0, weight=1)
        
        # Main clock (left side)
        self.main_clock = MainClockWidget(
            clock_frame,
            self.colors,
            main_tz,
            time_format=time_format,
            show_seconds=show_seconds
        )
        self.main_clock.grid(row=0, column=0, sticky="w", padx=(0, 20))
        
        # Secondary clocks container (right side)
        secondary_frame = tk.Frame(clock_frame, bg=self.colors.background)
        secondary_frame.grid(row=0, column=1, sticky="ne")
        
        # Secondary clock 1
        self.secondary_clock_1 = SecondaryClockWidget(
            secondary_frame,
            self.colors,
            sec_tz_1,
            time_format=time_format
        )
        self.secondary_clock_1.pack(pady=(0, 10))
        
        # Secondary clock 2
        self.secondary_clock_2 = SecondaryClockWidget(
            secondary_frame,
            self.colors,
            sec_tz_2,
            time_format=time_format
        )
        self.secondary_clock_2.pack()
    
    def _create_divider(self):
        """Create the divider with dots."""
        divider_frame = tk.Frame(self, bg=self.colors.background)
        divider_frame.grid(row=2, column=0, sticky="ew", pady=15)
        
        # Three dots
        dots_frame = tk.Frame(divider_frame, bg=self.colors.background)
        dots_frame.pack()
        
        for _ in range(3):
            dot = tk.Label(
                dots_frame,
                text="•",
                bg=self.colors.background,
                fg=self.colors.accent,
                font=("Helvetica", 12)
            )
            dot.pack(side=tk.LEFT, padx=3)
    
    def _create_weather_section(self):
        """Create the weather section with icon and temperature card."""
        weather_frame = tk.Frame(self, bg=self.colors.background)
        weather_frame.grid(row=3, column=0, sticky="nsew", padx=20, pady=10)
        
        # Configure columns
        weather_frame.grid_columnconfigure(0, weight=1)
        weather_frame.grid_columnconfigure(1, weight=1)
        weather_frame.grid_rowconfigure(0, weight=1)
        
        # Weather card (left side)
        self.weather_card = WeatherCardWidget(
            weather_frame,
            self.colors,
            icon_size=80
        )
        self.weather_card.grid(row=0, column=0, sticky="w", padx=(20, 10))
        
        # Temperature card (right side)
        self.temp_card = TemperatureCardWidget(
            weather_frame,
            self.colors,
            unit=self.temperature_unit,
            on_tap=self.on_temp_tap
        )
        self.temp_card.grid(row=0, column=1, sticky="e", padx=(10, 20))
    
    def _create_status_row(self):
        """Create the bottom status row."""
        status_frame = tk.Frame(self, bg=self.colors.background)
        status_frame.grid(row=4, column=0, sticky="sw", padx=15, pady=10)
        
        self.status_widget = StatusWidget(status_frame, self.colors)
        self.status_widget.pack(side=tk.LEFT)
    
    def update_weather(self, weather_data: WeatherData):
        """Update all weather displays with new data."""
        logger.debug("Updating main view with new weather data")
        
        # Update weather card
        self.weather_card.update_weather(
            weather_data.current,
            weather_data.location_name
        )
        
        # Update temperature card
        self.temp_card.update_weather(weather_data.current)
        
        # Update status
        self.status_widget.show_last_updated(weather_data.last_updated)
    
    def update_timezones(self, main_tz: TimezoneConfig,
                         sec_tz_1: TimezoneConfig,
                         sec_tz_2: TimezoneConfig):
        """Update the timezone configurations."""
        self.main_clock.update_timezone(main_tz)
        self.secondary_clock_1.update_timezone(sec_tz_1)
        self.secondary_clock_2.update_timezone(sec_tz_2)
    
    def show_offline_status(self):
        """Show offline indicator."""
        self.status_widget.show_offline()
    
    def show_updating_status(self):
        """Show updating indicator."""
        self.status_widget.show_updating()
