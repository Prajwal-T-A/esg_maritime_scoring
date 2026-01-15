"""
Live Emission Service

Wraps ML model inference with weather adjustment for real-time predictions.
Computes both baseline and weather-adjusted CO2 emissions.
"""

import logging
from typing import Dict, Tuple, Optional
from app.services.ml_service import predict_emissions

logger = logging.getLogger(__name__)


class LiveEmissionService:
    """Weather-adjusted ML inference for live tracking."""
    
    def __init__(self):
        """Initialize service."""
        pass
    
    def compute_adjusted_emissions(
        self,
        avg_speed: float,
        speed_std: float,
        distance_km: float,
        time_at_sea_hours: float,
        acceleration_events: int,
        length: float,
        width: float,
        draft: float,
        co2_factor: float,
        weather_resistance_factor: float = 1.0
    ) -> Dict[str, float]:
        """
        Compute baseline and weather-adjusted CO2 emissions.
        
        Parameters
        ----------
        avg_speed : float
            Average speed (knots)
        speed_std : float
            Speed std deviation (knots)
        distance_km : float
            Distance traveled (km)
        time_at_sea_hours : float
            Time at sea (hours)
        acceleration_events : int
            Count of acceleration events
        length : float
            Vessel length (m)
        width : float
            Vessel width (m)
        draft : float
            Vessel draft (m)
        co2_factor : float
            CO2 emission factor
        weather_resistance_factor : float
            Weather resistance multiplier (>=1.0)
        
        Returns
        -------
        dict
            {
                'base_co2_kg': float,
                'adjusted_co2_kg': float,
                'delta_due_to_weather': float,
                'adjusted_speed_knots': float
            }
        """
        # Get baseline prediction
        baseline_features = {
            'avg_speed': avg_speed,
            'speed_std': speed_std,
            'total_distance_km': distance_km,
            'time_at_sea_hours': time_at_sea_hours,
            'acceleration_events': acceleration_events,
            'length': length,
            'width': width,
            'draft': draft,
            'co2_factor': co2_factor
        }
        
        base_co2 = predict_emissions(baseline_features)
        
        # Compute weather-adjusted speed
        adjusted_speed = avg_speed * weather_resistance_factor
        
        # Get adjusted prediction with modified speed
        adjusted_features = baseline_features.copy()
        adjusted_features['avg_speed'] = adjusted_speed
        
        adjusted_co2 = predict_emissions(adjusted_features)
        
        delta = adjusted_co2 - base_co2
        
        return {
            'base_co2_kg': float(base_co2),
            'adjusted_co2_kg': float(adjusted_co2),
            'delta_due_to_weather': float(delta),
            'adjusted_speed_knots': float(adjusted_speed),
            'weather_resistance_factor': float(weather_resistance_factor)
        }


# Global instance
_live_emission_service: Optional['LiveEmissionService'] = None


def get_live_emission_service() -> LiveEmissionService:
    """Get or create global live emission service instance."""
    global _live_emission_service
    if _live_emission_service is None:
        _live_emission_service = LiveEmissionService()
        logger.info("Live Emission Service initialized")
    return _live_emission_service


def compute_adjusted_emissions(
    avg_speed: float,
    speed_std: float,
    distance_km: float,
    time_at_sea_hours: float,
    acceleration_events: int,
    length: float,
    width: float,
    draft: float,
    co2_factor: float,
    weather_resistance_factor: float = 1.0
) -> Dict[str, float]:
    """Convenience function to compute adjusted emissions."""
    service = get_live_emission_service()
    return service.compute_adjusted_emissions(
        avg_speed=avg_speed,
        speed_std=speed_std,
        distance_km=distance_km,
        time_at_sea_hours=time_at_sea_hours,
        acceleration_events=acceleration_events,
        length=length,
        width=width,
        draft=draft,
        co2_factor=co2_factor,
        weather_resistance_factor=weather_resistance_factor
    )
