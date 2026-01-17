"""
Weather service for WeatherClock Pi.

Handles fetching weather data from Open-Meteo API with caching and retry logic.
"""

import logging
import time
from datetime import datetime, date
from typing import Optional, Tuple, List
import requests

from models.weather_data import (
    WeatherCondition, 
    CurrentWeather, 
    DailyForecast, 
    WeatherData
)


logger = logging.getLogger(__name__)


class WeatherServiceError(Exception):
    """Exception raised for weather service errors."""
    pass


class WeatherService:
    """
    Service for fetching weather data from Open-Meteo API.
    
    Open-Meteo is a free weather API that doesn't require an API key.
    Rate limit: 10,000 requests/day (more than sufficient for our use case).
    """
    
    BASE_URL = "https://api.open-meteo.com/v1/forecast"
    
    # Retry configuration
    MAX_RETRIES = 3
    RETRY_DELAYS = [5, 15, 45]  # Exponential backoff in seconds
    
    def __init__(self, latitude: float, longitude: float, 
                 temperature_unit: str = "fahrenheit",
                 timeout: int = 10):
        """
        Initialize the weather service.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            temperature_unit: 'fahrenheit' or 'celsius'
            timeout: Request timeout in seconds
        """
        self.latitude = latitude
        self.longitude = longitude
        self.temperature_unit = temperature_unit
        self.timeout = timeout
        
        # Cache for offline resilience
        self._cache: Optional[dict] = None
        self._cache_time: Optional[datetime] = None
        self._location_name: str = ""
    
    def set_location_name(self, name: str):
        """Set the location name for display."""
        self._location_name = name
    
    def _build_params(self) -> dict:
        """Build API request parameters."""
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "current": "temperature_2m,apparent_temperature,weather_code,relative_humidity_2m,is_day",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min",
            "temperature_unit": self.temperature_unit,
            "timezone": "auto",
            "forecast_days": 5
        }
    
    def _make_request(self) -> dict:
        """
        Make API request with retry logic.
        
        Returns:
            API response as dictionary
        
        Raises:
            WeatherServiceError: If all retries fail
        """
        last_error = None
        
        for attempt in range(self.MAX_RETRIES):
            try:
                logger.debug(f"Weather API request attempt {attempt + 1}")
                
                response = requests.get(
                    self.BASE_URL,
                    params=self._build_params(),
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                data = response.json()
                
                # Update cache
                self._cache = data
                self._cache_time = datetime.now()
                
                logger.info("Weather data fetched successfully")
                return data
                
            except requests.Timeout:
                last_error = "Request timed out"
                logger.warning(f"Weather API timeout (attempt {attempt + 1})")
                
            except requests.RequestException as e:
                last_error = str(e)
                logger.warning(f"Weather API error (attempt {attempt + 1}): {e}")
            
            # Wait before retry (if not last attempt)
            if attempt < self.MAX_RETRIES - 1:
                delay = self.RETRY_DELAYS[attempt]
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
        
        # All retries failed
        raise WeatherServiceError(f"Failed to fetch weather data after {self.MAX_RETRIES} attempts: {last_error}")
    
    def _parse_current_weather(self, current_data: dict) -> CurrentWeather:
        """Parse current weather from API response."""
        weather_code = current_data.get("weather_code", 0)
        
        return CurrentWeather(
            temperature=current_data["temperature_2m"],
            feels_like=current_data["apparent_temperature"],
            condition=WeatherCondition.from_wmo_code(weather_code),
            weather_code=weather_code,
            humidity=current_data.get("relative_humidity_2m"),
            timestamp=datetime.now(),
            is_day=bool(current_data.get("is_day", 1))
        )
    
    def _parse_daily_forecast(self, daily_data: dict) -> List[DailyForecast]:
        """Parse daily forecast from API response."""
        forecasts = []
        
        dates = daily_data.get("time", [])
        codes = daily_data.get("weather_code", [])
        highs = daily_data.get("temperature_2m_max", [])
        lows = daily_data.get("temperature_2m_min", [])
        
        for i in range(min(len(dates), 5)):
            try:
                forecast_date = date.fromisoformat(dates[i])
                forecast = DailyForecast.from_data(
                    forecast_date=forecast_date,
                    weather_code=codes[i],
                    high_temp=highs[i],
                    low_temp=lows[i]
                )
                forecasts.append(forecast)
            except (IndexError, ValueError) as e:
                logger.warning(f"Error parsing forecast day {i}: {e}")
        
        return forecasts
    
    def get_weather(self) -> WeatherData:
        """
        Fetch current weather and forecast.
        
        Returns:
            WeatherData containing current conditions and 5-day forecast
        
        Raises:
            WeatherServiceError: If fetching fails and no cache available
        """
        try:
            data = self._make_request()
            
            current = self._parse_current_weather(data.get("current", {}))
            forecast = self._parse_daily_forecast(data.get("daily", {}))
            
            return WeatherData(
                current=current,
                forecast=forecast,
                location_name=self._location_name,
                last_updated=datetime.now()
            )
            
        except WeatherServiceError:
            # Try to use cached data
            if self._cache:
                logger.warning("Using cached weather data")
                current = self._parse_current_weather(self._cache.get("current", {}))
                forecast = self._parse_daily_forecast(self._cache.get("daily", {}))
                
                return WeatherData(
                    current=current,
                    forecast=forecast,
                    location_name=self._location_name,
                    last_updated=self._cache_time or datetime.now()
                )
            
            # No cache available
            raise
    
    def get_weather_safe(self) -> Optional[WeatherData]:
        """
        Fetch weather data without raising exceptions.
        
        Returns:
            WeatherData if successful, None otherwise
        """
        try:
            return self.get_weather()
        except WeatherServiceError as e:
            logger.error(f"Weather fetch failed: {e}")
            return None
    
    def has_cached_data(self) -> bool:
        """Check if cached data is available."""
        return self._cache is not None
    
    def get_cache_age(self) -> Optional[float]:
        """Get age of cached data in seconds."""
        if self._cache_time:
            return (datetime.now() - self._cache_time).total_seconds()
        return None
