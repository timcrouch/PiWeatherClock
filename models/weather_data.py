"""
Weather data models for WeatherClock Pi.

Defines data structures for current weather conditions and daily forecasts.
"""

from dataclasses import dataclass
from datetime import datetime, date
from enum import Enum
from typing import Optional


class WeatherCondition(Enum):
    """Simplified weather condition categories."""
    SUNNY = "sunny"
    CLOUDY = "cloudy"
    RAIN = "rain"
    SNOW = "snow"
    
    @classmethod
    def from_wmo_code(cls, code: int) -> "WeatherCondition":
        """
        Map WMO weather code to simplified condition.
        
        WMO Weather Interpretation Codes:
        - 0, 1: Clear sky, mainly clear -> SUNNY
        - 2, 3, 45, 48: Partly cloudy, overcast, fog -> CLOUDY
        - 71, 73, 75, 77, 85, 86: Snow variants -> SNOW
        - All others (drizzle, rain, thunderstorm): -> RAIN
        """
        SUNNY_CODES = {0, 1}
        CLOUDY_CODES = {2, 3, 45, 48}
        SNOW_CODES = {71, 73, 75, 77, 85, 86}
        
        if code in SUNNY_CODES:
            return cls.SUNNY
        elif code in CLOUDY_CODES:
            return cls.CLOUDY
        elif code in SNOW_CODES:
            return cls.SNOW
        else:
            return cls.RAIN
    
    def get_display_text(self) -> str:
        """Get human-readable display text for the condition."""
        display_texts = {
            WeatherCondition.SUNNY: "Sunny",
            WeatherCondition.CLOUDY: "Cloudy",
            WeatherCondition.RAIN: "Rain",
            WeatherCondition.SNOW: "Snow",
        }
        return display_texts.get(self, "Unknown")


@dataclass
class CurrentWeather:
    """Current weather data."""
    temperature: float
    feels_like: float
    condition: WeatherCondition
    weather_code: int
    humidity: Optional[int]
    timestamp: datetime
    is_day: bool
    
    def get_temperature_display(self, unit: str = "fahrenheit") -> str:
        """Format temperature for display with unit symbol."""
        symbol = "°F" if unit == "fahrenheit" else "°C"
        return f"{self.temperature:.0f}{symbol}"
    
    def get_feels_like_display(self, unit: str = "fahrenheit") -> str:
        """Format feels-like temperature for display."""
        symbol = "°F" if unit == "fahrenheit" else "°C"
        return f"Feels like {self.feels_like:.0f}{symbol}"


@dataclass
class DailyForecast:
    """Daily forecast data."""
    date: date
    day_name: str
    high_temp: float
    low_temp: float
    condition: WeatherCondition
    weather_code: int
    
    @classmethod
    def from_data(cls, forecast_date: date, weather_code: int, 
                  high_temp: float, low_temp: float) -> "DailyForecast":
        """Create DailyForecast from raw data."""
        return cls(
            date=forecast_date,
            day_name=forecast_date.strftime("%A"),
            high_temp=high_temp,
            low_temp=low_temp,
            condition=WeatherCondition.from_wmo_code(weather_code),
            weather_code=weather_code
        )
    
    def get_high_display(self, unit: str = "fahrenheit") -> str:
        """Format high temperature for display."""
        symbol = "°F" if unit == "fahrenheit" else "°C"
        return f"{self.high_temp:.0f}{symbol}"
    
    def get_low_display(self, unit: str = "fahrenheit") -> str:
        """Format low temperature for display."""
        symbol = "°F" if unit == "fahrenheit" else "°C"
        return f"{self.low_temp:.0f}{symbol}"
    
    def is_today(self) -> bool:
        """Check if this forecast is for today."""
        return self.date == date.today()


@dataclass
class WeatherData:
    """Container for all weather data."""
    current: CurrentWeather
    forecast: list[DailyForecast]
    location_name: str
    last_updated: datetime
    
    def is_stale(self, max_age_seconds: int = 900) -> bool:
        """Check if weather data needs refreshing."""
        age = (datetime.now() - self.last_updated).total_seconds()
        return age > max_age_seconds
