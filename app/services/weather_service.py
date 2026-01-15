"""
Weather Service Module

Fetches real-time weather data from OpenWeatherMap API and computes
weather resistance factors for maritime operations.

Features:
- Fetches wind speed, direction, weather conditions, wave height
- Computes weather_resistance_factor based on wind and wave conditions
- Identifies storm and rough sea conditions
- Implements 10-minute grid-cell caching (0.25° resolution)
- Graceful fallback on API failures
"""

import os
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import aiohttp
import ssl
import certifi

logger = logging.getLogger(__name__)


class WeatherCache:
    """Grid-based weather cache with 10-minute TTL."""
    
    GRID_RESOLUTION = 0.25  # 0.25 degree cells
    CACHE_TTL_SECONDS = 600  # 10 minutes
    
    def __init__(self):
        self.cache: Dict[str, Dict] = {}
    
    def _get_grid_key(self, lat: float, lon: float) -> str:
        """Get cache key for a grid cell."""
        grid_lat = round(lat / self.GRID_RESOLUTION) * self.GRID_RESOLUTION
        grid_lon = round(lon / self.GRID_RESOLUTION) * self.GRID_RESOLUTION
        return f"{grid_lat:.2f},{grid_lon:.2f}"
    
    def get(self, lat: float, lon: float) -> Optional[Dict]:
        """Get cached weather for grid cell if still valid."""
        key = self._get_grid_key(lat, lon)
        entry = self.cache.get(key)
        
        if entry and datetime.utcnow() - entry['timestamp'] < timedelta(seconds=self.CACHE_TTL_SECONDS):
            logger.debug(f"Weather cache hit for {key}")
            return entry['data']
        
        return None
    
    def set(self, lat: float, lon: float, data: Dict) -> None:
        """Cache weather data for grid cell."""
        key = self._get_grid_key(lat, lon)
        self.cache[key] = {
            'data': data,
            'timestamp': datetime.utcnow()
        }
        logger.debug(f"Cached weather for {key}")


class WeatherService:
    """OpenWeatherMap API integration with caching and failover."""
    
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY", "")
        self.current_weather_url = "https://api.openweathermap.org/data/2.5/weather"
        self.cache = WeatherCache()
        self._session: Optional[aiohttp.ClientSession] = None
        
        if not self.api_key:
            logger.warning("OPENWEATHER_API_KEY not set. Weather service will use defaults.")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create async HTTP session with SSL support."""
        if self._session is None:
            # Create SSL context for certificate verification
            ssl_context = ssl.create_default_context(cafile=certifi.where())
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            self._session = aiohttp.ClientSession(connector=connector)
        return self._session
    
    async def close(self):
        """Close HTTP session."""
        if self._session:
            await self._session.close()
    
    async def fetch_weather(
        self, 
        lat: float, 
        lon: float,
        timeout: float = 5.0
    ) -> Dict:
        """
        Fetch weather data for location.
        
        Parameters
        ----------
        lat : float
            Latitude
        lon : float
            Longitude
        timeout : float
            Request timeout in seconds
        
        Returns
        -------
        dict
            Weather data with keys:
            - wind_speed_ms (m/s)
            - wind_direction_deg (0-360)
            - condition (clear/rain/storm/clouds)
            - wave_height_m (float, may be None)
            - timestamp (ISO string)
            - weather_resistance_factor (float)
            - storm_flag (bool)
            - rough_sea_flag (bool)
        """
        # Try cache first
        cached = self.cache.get(lat, lon)
        if cached:
            return cached
        
        # If API key not set, use defaults
        if not self.api_key:
            logger.warning(f"No API key set. Using default weather for {lat}, {lon}")
            return self._get_default_weather()
        
        try:
            session = await self._get_session()
            
            # Try OneCall API (includes more comprehensive data)
            weather_data = await self._fetch_from_api(
                session, 
                lat, 
                lon, 
                timeout
            )
            
            if weather_data:
                # Cache the result
                self.cache.set(lat, lon, weather_data)
                return weather_data
        
        except asyncio.TimeoutError:
            logger.warning(f"Weather API timeout for {lat}, {lon}")
        except Exception as e:
            logger.error(f"Weather API error for {lat}, {lon}: {str(e)}")
        
        # Fallback to defaults
        logger.warning(f"Using default weather due to API failure for {lat}, {lon}")
        return self._get_default_weather()
    
    async def _fetch_from_api(
        self, 
        session: aiohttp.ClientSession, 
        lat: float, 
        lon: float,
        timeout: float
    ) -> Optional[Dict]:
        """Fetch weather from OpenWeatherMap API using free Current Weather endpoint."""
        try:
            # Use free Current Weather API 2.5
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            async with session.get(
                self.current_weather_url,
                params=params,
                timeout=aiohttp.ClientTimeout(total=5.0)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return self._parse_weather_response(data)
                else:
                    logger.warning(f"Weather API returned status {resp.status}")
                    return None
        
        except Exception as e:
            logger.error(f"Failed to fetch from weather API: {str(e)}")
            return None
    
    def _parse_weather_response(self, data: Dict) -> Dict:
        """Parse OpenWeatherMap Current Weather API response (2.5 free tier)."""
        try:
            # Extract current weather from free API response
            wind_data = data.get('wind', {})
            wind_speed = wind_data.get('speed', 0.0)  # m/s
            wind_deg = wind_data.get('deg', 0)
            
            weather_main = data.get('weather', [{}])[0].get('main', 'Clear').lower()
            
            # Free API doesn't provide wave data, estimate from wind
            # Rough approximation: 1m base + 0.1m per m/s wind speed
            wave_height = 1.0 + (wind_speed * 0.1) if wind_speed > 0 else 1.0
            
            # Compute factors
            weather_resistance_factor = self._compute_resistance_factor(wind_speed, wave_height)
            storm_flag = weather_main in ['thunderstorm', 'tornado']
            rough_sea_flag = wave_height > 3.0
            
            result = {
                'wind_speed_ms': float(wind_speed),
                'wind_direction_deg': int(wind_deg),
                'condition': weather_main,
                'wave_height_m': float(wave_height),
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'weather_resistance_factor': weather_resistance_factor,
                'storm_flag': storm_flag,
                'rough_sea_flag': bool(rough_sea_flag)
            }
            
            logger.debug(f"Parsed weather: wind={wind_speed}m/s, waves={wave_height}m")
            return result
        
        except Exception as e:
            logger.error(f"Failed to parse weather response: {str(e)}")
            return self._get_default_weather()
    
    def _compute_resistance_factor(
        self, 
        wind_speed_ms: float, 
        wave_height_m: Optional[float]
    ) -> float:
        """
        Compute weather resistance factor.
        
        base = 1.0
        +0.01 per m/s wind speed above 5 m/s
        +0.05 per meter wave height above 1m
        """
        factor = 1.0
        
        # Wind resistance
        if wind_speed_ms > 5.0:
            factor += 0.01 * (wind_speed_ms - 5.0)
        
        # Wave resistance
        if wave_height_m and wave_height_m > 1.0:
            factor += 0.05 * (wave_height_m - 1.0)
        
        return min(factor, 3.0)  # Cap at 3.0x
    
    def _get_default_weather(self) -> Dict:
        """Return sensible defaults when API unavailable."""
        return {
            'wind_speed_ms': 8.0,
            'wind_direction_deg': 180,
            'condition': 'cloudy',
            'wave_height_m': 1.5,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'weather_resistance_factor': 1.04,  # 1 + 0.01*4 (8m/s wind)
            'storm_flag': False,
            'rough_sea_flag': False
        }


# Global instance
_weather_service: Optional[WeatherService] = None


def get_weather_service() -> WeatherService:
    """Get or create global weather service instance."""
    global _weather_service
    if _weather_service is None:
        _weather_service = WeatherService()
    return _weather_service


async def fetch_weather(lat: float, lon: float) -> Dict:
    """Convenience function to fetch weather."""
    service = get_weather_service()
    return await service.fetch_weather(lat, lon)
