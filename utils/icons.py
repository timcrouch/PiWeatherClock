"""
Weather icon utilities for WeatherClock Pi.

Handles loading, caching, and mapping weather icons.
"""

import os
import logging
from pathlib import Path
from typing import Optional
from PIL import Image, ImageTk
from functools import lru_cache

from models.weather_data import WeatherCondition


logger = logging.getLogger(__name__)


def get_assets_directory() -> Path:
    """Get the assets directory path."""
    # Assets are relative to the package root
    return Path(__file__).parent.parent / "assets"


def get_icon_path(condition: WeatherCondition, is_day: bool = True) -> Path:
    """
    Get the icon file path for a weather condition.
    
    Args:
        condition: The weather condition
        is_day: Whether it's daytime (affects sunny icon)
    
    Returns:
        Path to the icon file
    """
    icons_dir = get_assets_directory() / "icons"
    
    # Map conditions to icon filenames
    icon_map = {
        WeatherCondition.SUNNY: "sunny_day.png" if is_day else "sunny_night.png",
        WeatherCondition.CLOUDY: "cloudy.png",
        WeatherCondition.RAIN: "rain.png",
        WeatherCondition.SNOW: "snow.png",
    }
    
    filename = icon_map.get(condition, "cloudy.png")
    return icons_dir / filename


class IconManager:
    """Manages weather icon loading and caching."""
    
    def __init__(self):
        self._cache: dict[str, ImageTk.PhotoImage] = {}
        self._pil_cache: dict[str, Image.Image] = {}
    
    def _get_cache_key(self, condition: WeatherCondition, is_day: bool, size: int) -> str:
        """Generate cache key for an icon."""
        return f"{condition.value}_{is_day}_{size}"
    
    def load_icon(self, condition: WeatherCondition, is_day: bool = True, 
                  size: int = 128) -> Optional[ImageTk.PhotoImage]:
        """
        Load and cache a weather icon.
        
        Args:
            condition: Weather condition
            is_day: Whether it's daytime
            size: Icon size in pixels (square)
        
        Returns:
            PhotoImage for use in Tkinter, or None if loading fails
        """
        cache_key = self._get_cache_key(condition, is_day, size)
        
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        icon_path = get_icon_path(condition, is_day)
        
        try:
            if not icon_path.exists():
                logger.warning(f"Icon not found: {icon_path}")
                return None
            
            # Load and resize image
            image = Image.open(icon_path)
            image = image.resize((size, size), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(image)
            
            # Cache and return
            self._cache[cache_key] = photo
            return photo
            
        except Exception as e:
            logger.error(f"Error loading icon {icon_path}: {e}")
            return None
    
    def load_pil_image(self, condition: WeatherCondition, is_day: bool = True,
                       size: int = 128) -> Optional[Image.Image]:
        """
        Load a weather icon as PIL Image (useful before Tk is initialized).
        
        Args:
            condition: Weather condition
            is_day: Whether it's daytime
            size: Icon size in pixels
        
        Returns:
            PIL Image, or None if loading fails
        """
        cache_key = f"pil_{self._get_cache_key(condition, is_day, size)}"
        
        if cache_key in self._pil_cache:
            return self._pil_cache[cache_key]
        
        icon_path = get_icon_path(condition, is_day)
        
        try:
            if not icon_path.exists():
                return None
            
            image = Image.open(icon_path)
            image = image.resize((size, size), Image.Resampling.LANCZOS)
            
            self._pil_cache[cache_key] = image
            return image
            
        except Exception as e:
            logger.error(f"Error loading PIL image {icon_path}: {e}")
            return None
    
    def clear_cache(self):
        """Clear the icon cache."""
        self._cache.clear()
        self._pil_cache.clear()
        logger.debug("Icon cache cleared")


# Global icon manager instance
_icon_manager: Optional[IconManager] = None


def get_icon_manager() -> IconManager:
    """Get the global icon manager instance."""
    global _icon_manager
    if _icon_manager is None:
        _icon_manager = IconManager()
    return _icon_manager
