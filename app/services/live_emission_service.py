"""
Live Emission Service
Computes weather-adjusted CO2 emissions for real-time vessel tracking.
"""

import logging
from typing import Dict
from app.services.ml_service import predict_emissions

logger = logging.getLogger(__name__)


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
) -> Dict:
    """
    Compute both baseline and weather-adjusted CO2 emissions.
    
    Parameters
    ----------
    avg_speed : float
        Average speed in knots
    speed_std : float
        Speed standard deviation
    distance_km : float
        Total distance traveled
    time_at_sea_hours : float
        Time at sea
    acceleration_events : int
        Number of acceleration events
    length, width, draft : float
        Vessel dimensions
    co2_factor : float
        Base CO2 emission factor
    weather_resistance_factor : float
        Weather resistance multiplier (>= 1.0)
    
    Returns
    -------
    dict
        base_co2_kg: Baseline emissions
        adjusted_co2_kg: Weather-adjusted emissions
        delta_due_to_weather: Additional emissions from weather
        resistance_factor: Applied weather factor
    """
    try:
        # Compute baseline emissions (no weather adjustment)
        base_features = {
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
        base_co2 = predict_emissions(base_features)
        
        # Compute weather-adjusted emissions
        # Increased resistance means more fuel consumption
        adjusted_speed_factor = weather_resistance_factor ** 0.5
        adjusted_features = {
            'avg_speed': avg_speed * adjusted_speed_factor,
            'speed_std': speed_std,
            'total_distance_km': distance_km,
            'time_at_sea_hours': time_at_sea_hours,
            'acceleration_events': acceleration_events,
            'length': length,
            'width': width,
            'draft': draft,
            'co2_factor': co2_factor * weather_resistance_factor
        }
        adjusted_co2 = predict_emissions(adjusted_features)
        
        delta = adjusted_co2 - base_co2
        
        return {
            "base_co2_kg": round(base_co2, 2),
            "adjusted_co2_kg": round(adjusted_co2, 2),
            "delta_due_to_weather": round(delta, 2),
            "resistance_factor": round(weather_resistance_factor, 3),
            "weather_impact_percent": round((delta / base_co2 * 100) if base_co2 > 0 else 0, 1)
        }
    
    except Exception as e:
        logger.error(f"Error computing adjusted emissions: {e}")
        # Return safe defaults
        return {
            "base_co2_kg": 0.0,
            "adjusted_co2_kg": 0.0,
            "delta_due_to_weather": 0.0,
            "resistance_factor": weather_resistance_factor,
            "weather_impact_percent": 0.0
        }
