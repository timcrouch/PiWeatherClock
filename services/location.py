"""
Location service for WeatherClock Pi.

Handles location detection and coordinate management.
"""

import logging
import requests
from typing import Optional, Tuple
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class LocationInfo:
    """Location information."""
    latitude: float
    longitude: float
    name: str
    timezone: str


class LocationService:
    """Service for location detection and management."""
    
    IP_API_URL = "http://ip-api.com/json/"
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self._cached_location: Optional[LocationInfo] = None
    
    def detect_location(self) -> Optional[LocationInfo]:
        """
        Detect location based on IP address.
        
        Uses the free ip-api.com service for approximate geolocation.
        
        Returns:
            LocationInfo if successful, None otherwise
        """
        try:
            logger.info("Attempting to auto-detect location...")
            
            response = requests.get(
                self.IP_API_URL,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("status") != "success":
                logger.warning(f"IP-API returned non-success status: {data.get('message')}")
                return None
            
            location = LocationInfo(
                latitude=data["lat"],
                longitude=data["lon"],
                name=f"{data.get('city', '')}, {data.get('regionName', '')}",
                timezone=data.get("timezone", "UTC")
            )
            
            self._cached_location = location
            logger.info(f"Location detected: {location.name} ({location.latitude}, {location.longitude})")
            
            return location
            
        except requests.Timeout:
            logger.error("Location detection timed out")
            return None
        except requests.RequestException as e:
            logger.error(f"Error detecting location: {e}")
            return None
        except (KeyError, ValueError) as e:
            logger.error(f"Error parsing location response: {e}")
            return None
    
    def get_location(self, config_lat: Optional[float] = None, 
                     config_lon: Optional[float] = None,
                     config_name: str = "") -> Optional[LocationInfo]:
        """
        Get location from config or auto-detect.
        
        Args:
            config_lat: Latitude from configuration
            config_lon: Longitude from configuration
            config_name: Location name from configuration
        
        Returns:
            LocationInfo if available, None otherwise
        """
        # Use configured coordinates if available
        if config_lat is not None and config_lon is not None:
            logger.info(f"Using configured location: {config_name or 'unnamed'}")
            return LocationInfo(
                latitude=config_lat,
                longitude=config_lon,
                name=config_name or "Configured Location",
                timezone="auto"  # Let the weather API determine timezone
            )
        
        # Try cached location
        if self._cached_location:
            return self._cached_location
        
        # Auto-detect
        return self.detect_location()
    
    def get_coordinates(self, config_lat: Optional[float] = None,
                        config_lon: Optional[float] = None) -> Optional[Tuple[float, float]]:
        """
        Get just the coordinates.
        
        Returns:
            Tuple of (latitude, longitude) or None
        """
        location = self.get_location(config_lat, config_lon)
        if location:
            return (location.latitude, location.longitude)
        return None
