"""
Unified vessel analysis service combining ML predictions and ESG scoring.
"""

from typing import Dict, List, Tuple
from app.services.ml_service import predict_emissions
from app.services.ollama_service import ollama_service
from ml.esg.esg_scoring import compute_esg_score, get_score_interpretation


async def analyze_vessel(
    mmsi: str,
    avg_speed: float,
    speed_std: float,
    total_distance_km: float,
    time_at_sea_hours: float,
    acceleration_events: int,
    length: float,
    width: float,
    draft: float,
    co2_factor: float,
    include_ai_recommendation: bool = True
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
    
    # Step 4: Generate AI-powered recommendations using Ollama (Optional)
    recommendation = None
    if include_ai_recommendation:
        recommendation = await _generate_ai_recommendation(
            esg_score=esg_score,
            rating=interpretation['rating'],
            estimated_co2_kg=estimated_co2_kg,
            total_distance_km=total_distance_km,
            avg_speed=avg_speed,
            acceleration_events=acceleration_events,
            time_at_sea_hours=time_at_sea_hours,
            risk_flags=risk_flags
        )
    
    return {
        'mmsi': mmsi,
        'estimated_co2_kg': estimated_co2_kg,
        'esg_score': esg_score,
        'rating': interpretation['rating'],
        'description': interpretation['description'],
        'recommendation': recommendation,
        'risk_flags': risk_flags
    }


async def _generate_ai_recommendation(
    esg_score: int,
    rating: str,
    estimated_co2_kg: float,
    total_distance_km: float,
    avg_speed: float,
    acceleration_events: int,
    time_at_sea_hours: float,
    risk_flags: List[str]
) -> str:
    """
    Generate personalized AI recommendations using Ollama.
    
    Falls back to default recommendation if Ollama is unavailable.
    """
    # Calculate derived metrics
    co2_intensity = estimated_co2_kg / total_distance_km if total_distance_km > 0 else 0
    
    # Create a focused prompt for Ollama
    prompt = f"""Given this vessel's performance data, provide EXACTLY 2-3 brief, actionable recommendations to improve their environmental score. Keep each point under 15 words.

Current Performance:
- ESG Score: {esg_score}/100 ({rating})
- CO₂ Emissions: {estimated_co2_kg:.1f} kg
- Distance: {total_distance_km:.1f} km
- CO₂ Intensity: {co2_intensity:.2f} kg/km
- Average Speed: {avg_speed:.1f} knots
- Acceleration Events: {acceleration_events}
- Time at Sea: {time_at_sea_hours:.1f} hours

Risk Flags: {', '.join(risk_flags) if risk_flags else 'None'}

Format your response as a numbered list with 2-3 points only. Be specific and actionable. Focus on the biggest improvement opportunities."""

    try:
        # Call Ollama asynchronously
        result = await ollama_service.chat(prompt, None, use_system_prompt=False)
        
        if result.get('success'):
            response = result['message'].strip()
            # Limit to 2-3 bullet points if response is too long
            lines = [line.strip() for line in response.split('\n') if line.strip()]
            if len(lines) > 3:
                lines = lines[:3]
            return '\n'.join(lines)
        else:
            # Fallback to default
            return _get_default_recommendation(esg_score, risk_flags)
    except Exception as e:
        # Fallback to default if Ollama fails
        return _get_default_recommendation(esg_score, risk_flags)


def _get_default_recommendation(esg_score: int, risk_flags: List[str]) -> str:
    """Fallback recommendations when Ollama is unavailable."""
    if esg_score >= 90:
        return "Industry-leading practices. Share best practices with fleet."
    elif esg_score >= 70:
        return "Maintain current practices, minor optimizations possible."
    elif esg_score >= 50:
        return "Review operational practices. Focus on reducing identified risks."
    elif esg_score >= 30:
        return "Immediate action required. Implement fuel efficiency programs."
    else:
        return "Critical environmental performance. Urgent intervention needed."
