"""
Unified vessel analysis service combining ML predictions and ESG scoring.
"""

from typing import Dict, List, Tuple
from app.services.ml_service import predict_emissions
from ml.esg.esg_scoring import compute_esg_score, get_score_interpretation


def analyze_vessel(
    mmsi: str,
    avg_speed: float,
    speed_std: float,
    total_distance_km: float,
    time_at_sea_hours: float,
    acceleration_events: int,
    length: float,
    width: float,
    draft: float,
    co2_factor: float
) -> Dict:
    """
    Unified analysis combining ML emission prediction and ESG scoring.
    
    Parameters
    ----------
    mmsi : str
        Maritime Mobile Service Identity
    avg_speed : float
        Average speed over ground in knots
    speed_std : float
        Standard deviation of speed in knots
    total_distance_km : float
        Total distance traveled in kilometers
    time_at_sea_hours : float
        Total operational time in hours
    acceleration_events : int
        Count of significant speed change events
    length : float
        Vessel length in meters
    width : float
        Vessel width in meters
    draft : float
        Vessel draft in meters
    co2_factor : float
        CO₂ emission factor (kg CO₂ per fuel unit)
    
    Returns
    -------
    dict
        Complete vessel analysis including:
        - mmsi
        - estimated_co2_kg
        - esg_score
        - rating
        - description
        - recommendation
        - risk_flags
    """
    # Step 1: ML prediction
    features = {
        'avg_speed': avg_speed,
        'speed_std': speed_std,
        'total_distance_km': total_distance_km,
        'time_at_sea_hours': time_at_sea_hours,
        'acceleration_events': acceleration_events,
        'length': length,
        'width': width,
        'draft': draft,
        'co2_factor': co2_factor
    }
    
    estimated_co2_kg = predict_emissions(features)
    
    # Step 2: ESG scoring
    esg_score, risk_flags = compute_esg_score(
        baseline_co2=estimated_co2_kg,
        total_distance_km=total_distance_km,
        avg_speed=avg_speed,
        acceleration_events=acceleration_events,
        time_at_sea_hours=time_at_sea_hours
    )
    
    # Step 3: Interpretation
    interpretation = get_score_interpretation(esg_score)
    
    return {
        'mmsi': mmsi,
        'estimated_co2_kg': estimated_co2_kg,
        'esg_score': esg_score,
        'rating': interpretation['rating'],
        'description': interpretation['description'],
        'recommendation': interpretation['recommendation'],
        'risk_flags': risk_flags
    }
