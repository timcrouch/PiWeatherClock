"""
Main display controller for WeatherClock Pi.

Manages the application window, views, and weather data updates.
"""

import tkinter as tk
import logging
from typing import Optional

from models.weather_data import WeatherData
from services.weather import WeatherService
from services.location import LocationService
from utils.config import AppConfig, load_config
from gui.main_view import MainView
from gui.forecast_view import ForecastView
from gui.settings_dialog import SettingsDialog


logger = logging.getLogger(__name__)


class WeatherClockApp:
    """
    Main application class for WeatherClock Pi.
    
    Manages the Tkinter window, view switching, and weather data updates.
    """
    
    def __init__(self, config: Optional[AppConfig] = None, 
                 fullscreen: bool = True,
                 hide_cursor: bool = True):
        """
        Initialize the WeatherClock application.
        
        Args:
            config: Application configuration (loads from file if not provided)
            fullscreen: Whether to run in fullscreen mode
            hide_cursor: Whether to hide the mouse cursor
        """
        # Load configuration
        self.config = config or load_config()
        self.colors = self.config.get_theme_colors()
        
        # Services
        self.location_service = LocationService()
        self.weather_service: Optional[WeatherService] = None
        self.weather_data: Optional[WeatherData] = None
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("WeatherClock Pi")
        self.root.configure(bg=self.colors.background)
        
        # Configure fullscreen
        if fullscreen:
            self.root.attributes('-fullscreen', True)
        else:
            # Development mode: windowed at 800x480 (Pi display size)
            self.root.geometry("800x480")
        
        # Hide cursor for kiosk mode
        if hide_cursor:
            self.root.config(cursor='none')
        
        # Escape key to exit fullscreen (development)
        self.root.bind('<Escape>', self._handle_escape)
        
        # Track current view
        self._current_view = "main"
        
        # Initialize views
        self._init_views()
        
        # Schedule weather updates
        self._weather_update_job = None
    
    def _init_views(self):
        """Initialize the main and forecast views."""
        # Container for views
        self.view_container = tk.Frame(self.root, bg=self.colors.background)
        self.view_container.pack(fill=tk.BOTH, expand=True)
        
        # Main view with multi-timezone clocks
        self.main_view = MainView(
            self.view_container,
            self.colors,
            main_timezone=self.config.main_timezone,
            secondary_timezone_1=self.config.secondary_timezone_1,
            secondary_timezone_2=self.config.secondary_timezone_2,
            time_format=self.config.display.time_format,
            show_seconds=self.config.display.show_seconds,
            temperature_unit=self.config.display.temperature_unit,
            on_temp_tap=self._show_forecast,
            on_settings_tap=self._show_settings
        )
        
        # Forecast view
        self.forecast_view = ForecastView(
            self.view_container,
            self.colors,
            temperature_unit=self.config.display.temperature_unit,
            timeout_seconds=self.config.refresh.forecast_timeout,
            on_close=self._show_main
        )
        
        # Show main view initially
        self._show_main()
    
    def _show_main(self):
        """Switch to the main view."""
        logger.debug("Switching to main view")
        self.forecast_view.pack_forget()
        self.forecast_view.hide()
        self.main_view.pack(fill=tk.BOTH, expand=True)
        self._current_view = "main"
    
    def _show_forecast(self):
        """Switch to the forecast view."""
        if self.weather_data and self.weather_data.forecast:
            logger.info("Switching to forecast view")
            self.main_view.pack_forget()
            self.forecast_view.pack(fill=tk.BOTH, expand=True)
            self.forecast_view.show(self.weather_data.forecast)
            self._current_view = "forecast"
        else:
            logger.warning("No forecast data available to display")
    
    def _show_settings(self):
        """Open the settings dialog."""
        logger.info("Opening settings dialog")
        
        SettingsDialog(
            self.root,
            self.colors,
            self.config,
            on_save=self._on_settings_save
        )
    
    def _on_settings_save(self, updated_config: AppConfig):
        """Handle settings save - update the clock displays."""
        logger.info("Settings saved, updating clocks")
        self.config = updated_config
        
        # Update main view with new timezones
        self.main_view.update_timezones(
            self.config.main_timezone,
            self.config.secondary_timezone_1,
            self.config.secondary_timezone_2
        )
    
    def _handle_escape(self, event):
        """Handle escape key press."""
        if self.root.attributes('-fullscreen'):
            # Exit fullscreen
            self.root.attributes('-fullscreen', False)
            self.root.geometry("800x480")
        else:
            # In windowed mode, exit application
            self.stop()
    
    def _init_weather_service(self) -> bool:
        """Initialize the weather service with location."""
        location = self.location_service.get_location(
            self.config.location.latitude,
            self.config.location.longitude,
            self.config.location.name
        )
        
        if not location:
            logger.error("Could not determine location")
            return False
        
        self.weather_service = WeatherService(
            latitude=location.latitude,
            longitude=location.longitude,
            temperature_unit=self.config.display.temperature_unit
        )
        self.weather_service.set_location_name(location.name)
        
        logger.info(f"Weather service initialized for {location.name}")
        return True
    
    def _update_weather(self):
        """Fetch and update weather data."""
        if not self.weather_service:
            if not self._init_weather_service():
                logger.error("Failed to initialize weather service")
                self._schedule_weather_update()
                return
        
        logger.info("Fetching weather data...")
        
        if self._current_view == "main":
            self.main_view.show_updating_status()
        
        # Fetch weather data
        weather_data = self.weather_service.get_weather_safe()
        
        if weather_data:
            self.weather_data = weather_data
            
            # Update views
            if self._current_view == "main":
                self.main_view.update_weather(weather_data)
            
            logger.info("Weather data updated successfully")
        else:
            logger.warning("Failed to fetch weather data")
            if self._current_view == "main":
                self.main_view.show_offline_status()
        
        # Schedule next update
        self._schedule_weather_update()
    
    def _schedule_weather_update(self):
        """Schedule the next weather data update."""
        interval_ms = self.config.refresh.weather_interval * 1000
        self._weather_update_job = self.root.after(interval_ms, self._update_weather)
        logger.debug(f"Next weather update in {self.config.refresh.weather_interval} seconds")
    
    def run(self):
        """Start the application."""
        logger.info("Starting WeatherClock Pi")
        
        # Initial weather fetch
        self.root.after(100, self._update_weather)
        
        # Run the main loop
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
            self.stop()
    
    def stop(self):
        """Stop the application."""
        logger.info("Stopping WeatherClock Pi")
        
        if self._weather_update_job:
            self.root.after_cancel(self._weather_update_job)
        
        self.root.quit()
        self.root.destroy()
