"""
Weather Service Module
Fetches real-time weather data and computes resistance factors for maritime operations.
"""

import os
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import aiohttp

logger = logging.getLogger(__name__)

class WeatherCache:
    """Grid-based weather cache with 10-minute TTL."""
    
    def __init__(self, grid_size: float = 0.25, ttl_minutes: int = 10):
        self.grid_size = grid_size
        self.ttl = timedelta(minutes=ttl_minutes)
        self.cache: Dict[Tuple[float, float], Tuple[Dict, datetime]] = {}
    
    def _grid_key(self, lat: float, lon: float) -> Tuple[float, float]:
        """Round coordinates to grid cell."""
        grid_lat = round(lat / self.grid_size) * self.grid_size
        grid_lon = round(lon / self.grid_size) * self.grid_size
        return (grid_lat, grid_lon)
    
    def get(self, lat: float, lon: float) -> Optional[Dict]:
        """Retrieve cached weather if not expired."""
        key = self._grid_key(lat, lon)
        if key in self.cache:
            data, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.ttl:
                logger.debug(f"Cache hit for grid {key}")
                return data
            else:
                del self.cache[key]
        return None
    
    def set(self, lat: float, lon: float, data: Dict):
        """Cache weather data."""
        key = self._grid_key(lat, lon)
        self.cache[key] = (data, datetime.now())
        logger.debug(f"Cached weather for grid {key}")


class WeatherService:
    """Fetches and processes weather data for maritime operations."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENWEATHER_API_KEY")
        self.cache = WeatherCache()
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        
        if not self.api_key:
            logger.warning("OPENWEATHER_API_KEY not set. Weather features will use defaults.")
    
    async def fetch_weather(self, lat: float, lon: float) -> Dict:
        """
        Fetch weather data for coordinates and compute resistance factors.
        
        Returns:
            dict with wind_speed_ms, wind_direction_deg, weather_condition,
            wave_height_m, weather_resistance_factor, storm_flag, rough_sea_flag
        """
        # Check cache first
        cached = self.cache.get(lat, lon)
        if cached:
            return cached
        
        # If no API key, return default values
        if not self.api_key:
            return self._default_weather()
        
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "lat": lat,
                    "lon": lon,
                    "appid": self.api_key,
                    "units": "metric"
                }
                
                async with session.get(self.base_url, params=params, timeout=5) as response:
                    if response.status != 200:
                        logger.error(f"OpenWeather API error: {response.status}")
                        return self._default_weather()
                    
                    data = await response.json()
                    weather_data = self._process_weather_data(data)
                    
                    # Cache the result
                    self.cache.set(lat, lon, weather_data)
                    
                    return weather_data
        
        except asyncio.TimeoutError:
            logger.error("Weather API timeout")
            return self._default_weather()
        except Exception as e:
            logger.error(f"Weather fetch error: {e}")
            return self._default_weather()
    
    def _process_weather_data(self, data: Dict) -> Dict:
        """Process OpenWeather API response."""
        try:
            # Extract wind data
            wind_speed = data.get("wind", {}).get("speed", 0.0)  # m/s
            wind_direction = data.get("wind", {}).get("deg", 0.0)
            
            # Extract weather condition
            weather_main = data.get("weather", [{}])[0].get("main", "Clear")
            weather_desc = data.get("weather", [{}])[0].get("description", "clear sky")
            
            # Wave height estimation (OpenWeather doesn't provide directly)
            # Estimate from wind speed using empirical formula
            wave_height = self._estimate_wave_height(wind_speed)
            
            # Compute resistance factor
            resistance_factor = self._compute_resistance_factor(wind_speed, wave_height)
            
            # Determine flags
            storm_flag = weather_main.lower() in ["thunderstorm", "squall", "tornado"]
            rough_sea_flag = wave_height > 2.5 or wind_speed > 15.0
            
            return {
                "wind_speed_ms": round(wind_speed, 2),
                "wind_direction_deg": round(wind_direction, 1),
                "weather_condition": weather_main,
                "weather_description": weather_desc,
                "wave_height_m": round(wave_height, 2),
                "weather_resistance_factor": round(resistance_factor, 3),
                "storm_flag": storm_flag,
                "rough_sea_flag": rough_sea_flag,
                "temperature_c": data.get("main", {}).get("temp", 20.0),
                "humidity_percent": data.get("main", {}).get("humidity", 70)
            }
        
        except Exception as e:
            logger.error(f"Error processing weather data: {e}")
            return self._default_weather()
    
    def _estimate_wave_height(self, wind_speed_ms: float) -> float:
        """
        Estimate significant wave height from wind speed.
        Using simplified Beaufort scale correlation.
        """
        if wind_speed_ms < 3:
            return 0.1
        elif wind_speed_ms < 7:
            return 0.5
        elif wind_speed_ms < 12:
            return 1.5
        elif wind_speed_ms < 17:
            return 3.0
        elif wind_speed_ms < 21:
            return 5.0
        else:
            return 7.0
    
    def _compute_resistance_factor(self, wind_speed_ms: float, wave_height_m: float) -> float:
        """
        Compute weather resistance factor for vessel operations.
        
        Base = 1.0
        +0.01 per m/s wind above 5 m/s
        +0.05 per meter wave height above 1m
        """
        factor = 1.0
        
        # Wind contribution
        if wind_speed_ms > 5.0:
            factor += (wind_speed_ms - 5.0) * 0.01
        
        # Wave contribution
        if wave_height_m > 1.0:
            factor += (wave_height_m - 1.0) * 0.05
        
        return max(1.0, min(factor, 2.0))  # Cap between 1.0 and 2.0
    
    def _default_weather(self) -> Dict:
        """Return default weather values when API is unavailable."""
        return {
            "wind_speed_ms": 8.0,
            "wind_direction_deg": 180.0,
            "weather_condition": "Clear",
            "weather_description": "clear sky",
            "wave_height_m": 1.2,
            "weather_resistance_factor": 1.04,
            "storm_flag": False,
            "rough_sea_flag": False,
            "temperature_c": 20.0,
            "humidity_percent": 70
        }


# Global instance
_weather_service = None

def get_weather_service() -> WeatherService:
    """Get or create weather service singleton."""
    global _weather_service
    if _weather_service is None:
        _weather_service = WeatherService()
    return _weather_service

async def fetch_weather(lat: float, lon: float) -> Dict:
    """Convenience function to fetch weather."""
    service = get_weather_service()
    return await service.fetch_weather(lat, lon)
