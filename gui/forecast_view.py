"""
Forecast view for WeatherClock Pi.

Displays 5-day weather forecast with auto-return functionality.
"""

import tkinter as tk
import logging
from typing import Callable, Optional, List

from models.weather_data import DailyForecast
from utils.config import ThemeColors
from gui.widgets import ForecastDayWidget


logger = logging.getLogger(__name__)


class ForecastView(tk.Frame):
    """
    5-day forecast overlay view.
    
    Displays forecasts horizontally with auto-return to main view.
    Touch anywhere to return immediately.
    """
    
    def __init__(self, parent, colors: ThemeColors,
                 temperature_unit: str = "fahrenheit",
                 timeout_seconds: int = 30,
                 on_close: Optional[Callable] = None,
                 **kwargs):
        super().__init__(parent, bg=colors.background, **kwargs)
        
        self.colors = colors
        self.temperature_unit = temperature_unit
        self.timeout_seconds = timeout_seconds
        self.on_close = on_close
        
        self._timeout_job = None
        self._countdown_job = None
        self._remaining_seconds = timeout_seconds
        
        self.day_widgets: List[ForecastDayWidget] = []
        
        # Configure layout
        self.grid_rowconfigure(0, weight=1)  # Forecast area
        self.grid_rowconfigure(1, weight=0)  # Bottom bar
        self.grid_columnconfigure(0, weight=1)
        
        self._create_forecast_area()
        self._create_bottom_bar()
        
        # Bind touch anywhere to close
        self.bind('<Button-1>', self._handle_tap)
    
    def _create_forecast_area(self):
        """Create the 5-day forecast display area."""
        self.forecast_frame = tk.Frame(self, bg=self.colors.background)
        self.forecast_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # Configure 5 equal columns
        for i in range(5):
            self.forecast_frame.grid_columnconfigure(i, weight=1)
        self.forecast_frame.grid_rowconfigure(0, weight=1)
        
        # Create 5 day widgets (will be updated with data)
        for i in range(5):
            day_widget = ForecastDayWidget(
                self.forecast_frame,
                self.colors,
                is_today=(i == 0),
                icon_size=64
            )
            day_widget.grid(row=0, column=i, sticky="nsew", padx=10, pady=10)
            day_widget.bind('<Button-1>', self._handle_tap)
            self.day_widgets.append(day_widget)
    
    def _create_bottom_bar(self):
        """Create bottom bar with hint and countdown."""
        bottom_frame = tk.Frame(self, bg=self.colors.background)
        bottom_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        # Tap to return hint
        hint_label = tk.Label(
            bottom_frame,
            text="Tap anywhere to return",
            bg=self.colors.background,
            fg=self.colors.accent,
            font=("Roboto", 14)
        )
        hint_label.pack(side=tk.LEFT)
        hint_label.bind('<Button-1>', self._handle_tap)
        
        # Countdown timer
        self.countdown_label = tk.Label(
            bottom_frame,
            text="",
            bg=self.colors.background,
            fg=self.colors.secondary_text,
            font=("Roboto", 12)
        )
        self.countdown_label.pack(side=tk.RIGHT)
    
    def _handle_tap(self, event):
        """Handle tap to close the forecast view."""
        logger.debug("Forecast view tapped, closing")
        self._close()
    
    def _close(self):
        """Close the forecast view."""
        self._cancel_timers()
        
        if self.on_close:
            self.on_close()
    
    def _cancel_timers(self):
        """Cancel any pending timer jobs."""
        if self._timeout_job:
            self.after_cancel(self._timeout_job)
            self._timeout_job = None
        
        if self._countdown_job:
            self.after_cancel(self._countdown_job)
            self._countdown_job = None
    
    def _start_auto_return_timer(self):
        """Start the auto-return countdown."""
        self._remaining_seconds = self.timeout_seconds
        self._update_countdown()
    
    def _update_countdown(self):
        """Update the countdown display."""
        if self._remaining_seconds > 0:
            self.countdown_label.config(
                text=f"Auto-return in {self._remaining_seconds}s"
            )
            self._remaining_seconds -= 1
            self._countdown_job = self.after(1000, self._update_countdown)
        else:
            self._close()
    
    def update_forecast(self, forecasts: List[DailyForecast]):
        """Update the forecast display with new data."""
        logger.debug(f"Updating forecast view with {len(forecasts)} days")
        
        for i, forecast in enumerate(forecasts[:5]):
            if i < len(self.day_widgets):
                self.day_widgets[i].update_forecast(forecast, self.temperature_unit)
    
    def show(self, forecasts: List[DailyForecast]):
        """Show the forecast view and start auto-return timer."""
        logger.info("Showing forecast view")
        
        # Update data
        self.update_forecast(forecasts)
        
        # Start auto-return timer
        self._start_auto_return_timer()
    
    def hide(self):
        """Hide the forecast view."""
        self._cancel_timers()
