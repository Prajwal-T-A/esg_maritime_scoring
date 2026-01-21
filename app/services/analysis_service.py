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
    include_ai_recommendation: bool = True,
    generate_report: bool = False
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
    
    # Step 5: Generate Detailed Report (Optional)
    detailed_report = None
    if generate_report:
        detailed_report = await _generate_detailed_report(
            mmsi=mmsi,
            esg_score=esg_score,
            rating=interpretation['rating'],
            estimated_co2_kg=estimated_co2_kg,
            total_distance_km=total_distance_km,
            avg_speed=avg_speed,
            risk_flags=risk_flags
        )

    return {
        'mmsi': mmsi,
        'estimated_co2_kg': estimated_co2_kg,
        'esg_score': esg_score,
        'rating': interpretation['rating'],
        'description': interpretation['description'],
        'recommendation': recommendation,
        'detailed_report': detailed_report,
        'risk_flags': risk_flags
    }


async def _generate_detailed_report(
    mmsi: str,
    esg_score: int,
    rating: str,
    estimated_co2_kg: float,
    total_distance_km: float,
    avg_speed: float,
    risk_flags: List[str]
) -> str:
    """Generate a comprehensive markdown report using Ollama."""
    try:
        co2_intensity = estimated_co2_kg / total_distance_km if total_distance_km > 0 else 0
        prompt = f"""Generate a professional Environmental Impact Assessment Report in Markdown for Vessel {mmsi}.
        
Data:
- ESG Score: {esg_score}/100 ({rating})
- Total CO2 Emissions: {estimated_co2_kg:.2f} kg
- Carbon Intensity: {co2_intensity:.2f} kg/km
- Operating Speed: {avg_speed:.1f} knots
- Active Risks: {', '.join(risk_flags) if risk_flags else 'None'}

Required Structure:
1. **Executive Summary**: Brief overview of the vessel's environmental performance.
2. **Analysis of Key Metrics**: detailed breakdown of the emissions and intensity.
3. **Risk Assessment**: Discussion of the flagged risks and their potential impact.
4. **Regulatory Recommendations**: Suggestions for compliance (IMO, CII).
5. **Action Plan**: 3 concrete steps to improve the score.

Keep it professional, concise, and structured."""

        result = await ollama_service.chat(prompt, None, use_system_prompt=False)
        return result['message'] if result.get('success') else "Failed to generate report."
    except Exception as e:
        return f"Error generating report: {str(e)}"


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


async def analyze_fleet(vessels: List[Dict], selected_port: str = "all") -> Dict:
    """
    Generate comprehensive fleet analysis report.
    
    Parameters
    ----------
    vessels : List[Dict]
        List of vessel data dictionaries
    selected_port : str
        Port/sector filter (default: "all")
    
    Returns
    -------
    dict
        Complete fleet analysis with aggregated metrics and detailed report
    """
    from datetime import datetime
    
    # Filter vessels by port if needed
    if selected_port != "all":
        filtered_vessels = [v for v in vessels if v.get('sector') == selected_port]
    else:
        filtered_vessels = vessels
    
    if not filtered_vessels:
        return {
            'total_vessels': 0,
            'total_emissions_kg': 0,
            'average_esg_score': 0,
            'total_distance_km': 0,
            'detailed_report': "No vessels available for analysis.",
            'timestamp': datetime.utcnow().isoformat() + "Z"
        }
    
    # Calculate aggregate statistics
    total_vessels = len(filtered_vessels)
    total_emissions = sum(
        v.get('estimated_co2_kg', 0) + v.get('delta_weather', 0) 
        for v in filtered_vessels
    )
    average_esg = sum(v.get('esg_score', 0) for v in filtered_vessels) / total_vessels
    total_distance = sum(v.get('total_distance_km', 0) for v in filtered_vessels)
    
    # Calculate weather impact
    total_weather_impact = sum(v.get('delta_weather', 0) for v in filtered_vessels)
    base_emissions = total_emissions - total_weather_impact
    weather_impact_percentage = (total_weather_impact / base_emissions * 100) if base_emissions > 0 else 0
    
    # Calculate average weather conditions
    vessels_with_weather = [v for v in filtered_vessels if v.get('weather')]
    avg_wind_speed = 0
    avg_wave_height = 0
    if vessels_with_weather:
        avg_wind_speed = sum(v.get('weather', {}).get('wind_speed_ms', 0) for v in vessels_with_weather) / len(vessels_with_weather)
        avg_wave_height = sum(v.get('weather', {}).get('wave_height_m', 0) for v in vessels_with_weather) / len(vessels_with_weather)
    
    # Categorize vessels by ESG score
    excellent = [v for v in filtered_vessels if v.get('esg_score', 0) >= 90]
    good = [v for v in filtered_vessels if 70 <= v.get('esg_score', 0) < 90]
    moderate = [v for v in filtered_vessels if 50 <= v.get('esg_score', 0) < 70]
    poor = [v for v in filtered_vessels if 30 <= v.get('esg_score', 0) < 50]
    critical = [v for v in filtered_vessels if v.get('esg_score', 0) < 30]
    
    # Find top and bottom performers
    sorted_vessels = sorted(filtered_vessels, key=lambda v: v.get('esg_score', 0), reverse=True)
    top_performers = sorted_vessels[:3]
    bottom_performers = sorted_vessels[-3:]
    
    # Calculate average emissions intensity
    avg_intensity = total_emissions / total_distance if total_distance > 0 else 0
    
    # Generate comprehensive report using Ollama
    detailed_report = await _generate_fleet_report(
        total_vessels=total_vessels,
        total_emissions=total_emissions,
        average_esg=average_esg,
        total_distance=total_distance,
        excellent_count=len(excellent),
        good_count=len(good),
        moderate_count=len(moderate),
        poor_count=len(poor),
        critical_count=len(critical),
        top_performers=top_performers,
        bottom_performers=bottom_performers,
        avg_intensity=avg_intensity,
        selected_port=selected_port,
        total_weather_impact=total_weather_impact,
        base_emissions=base_emissions,
        weather_impact_percentage=weather_impact_percentage,
        avg_wind_speed=avg_wind_speed,
        avg_wave_height=avg_wave_height
    )
    
    return {
        'total_vessels': total_vessels,
        'total_emissions_kg': total_emissions,
        'average_esg_score': average_esg,
        'total_distance_km': total_distance,
        'detailed_report': detailed_report,
        'timestamp': datetime.utcnow().isoformat() + "Z"
    }


async def _generate_fleet_report(
    total_vessels: int,
    total_emissions: float,
    average_esg: float,
    total_distance: float,
    excellent_count: int,
    good_count: int,
    moderate_count: int,
    poor_count: int,
    critical_count: int,
    top_performers: List[Dict],
    bottom_performers: List[Dict],
    avg_intensity: float,
    selected_port: str,
    total_weather_impact: float = 0,
    base_emissions: float = 0,
    weather_impact_percentage: float = 0,
    avg_wind_speed: float = 0,
    avg_wave_height: float = 0
) -> str:
    """Generate comprehensive fleet analysis report using Ollama."""
    try:
        # Prepare top and bottom performer summaries
        top_summary = ", ".join([
            f"{v.get('vessel_name', v.get('mmsi', 'Unknown'))} (ESG: {v.get('esg_score', 0)})"
            for v in top_performers
        ]) if top_performers else "N/A"
        
        bottom_summary = ", ".join([
            f"{v.get('vessel_name', v.get('mmsi', 'Unknown'))} (ESG: {v.get('esg_score', 0)})"
            for v in bottom_performers
        ]) if bottom_performers else "N/A"
        
        port_text = f"for {selected_port}" if selected_port != "all" else "across all ports"
        
        prompt = f"""Generate a comprehensive Professional Fleet Environmental Performance Report in Markdown format.

Fleet Overview {port_text}:
- Total Vessels: {total_vessels}
- Total CO₂ Emissions: {total_emissions:.2f} kg ({total_emissions/1000:.2f} tonnes)
- Base Emissions (without weather): {base_emissions:.2f} kg ({base_emissions/1000:.2f} tonnes)
- Weather Impact on Emissions: +{total_weather_impact:.2f} kg (+{total_weather_impact/1000:.2f} tonnes)
- Weather Impact Percentage: {weather_impact_percentage:.1f}% increase
- Average ESG Score: {average_esg:.1f}/100
- Total Distance Traveled: {total_distance:.2f} km ({total_distance/1.852:.0f} nautical miles)
- Average Carbon Intensity: {avg_intensity:.2f} kg CO₂/km

Weather Conditions:
- Average Wind Speed: {avg_wind_speed:.2f} m/s
- Average Wave Height: {avg_wave_height:.2f} m

Fleet Performance Distribution:
- Excellent (90-100): {excellent_count} vessels
- Good (70-89): {good_count} vessels
- Moderate (50-69): {moderate_count} vessels
- Poor (30-49): {poor_count} vessels
- Critical (<30): {critical_count} vessels

Top Performers: {top_summary}
Bottom Performers: {bottom_summary}

Required Structure:
# Fleet Environmental Performance Report

## 1. Executive Summary
Brief overview of overall fleet performance and key findings (2-3 paragraphs).

## 2. Fleet Metrics Analysis
Detailed breakdown of emissions, ESG scores, and performance distribution.

## 3. Weather Impact Analysis
Analysis of how weather conditions (wind speed, wave height) affected fleet emissions. Include the total additional CO₂ emissions caused by adverse weather and percentage impact.

## 4. Performance Distribution
Analysis of how vessels are distributed across ESG categories and what this means.

## 5. Top and Bottom Performers
Insights into what makes top performers successful and what challenges bottom performers face.

## 6. Fleet-Wide Recommendations
At least 5 specific, actionable recommendations to improve overall fleet performance.

## 7. Regulatory Compliance
Assessment of fleet compliance with IMO regulations (CII, EEXI) and upcoming requirements.

## 8. Action Plan
Concrete steps with timeline for implementation:
- Immediate actions (0-30 days)
- Short-term initiatives (1-3 months)
- Long-term strategies (3-12 months)

## 9. Expected Outcomes
Projected improvements in emissions and ESG scores if recommendations are implemented.

Keep the report professional, data-driven, and actionable. Use markdown formatting for clarity."""

        result = await ollama_service.chat(prompt, None, use_system_prompt=False)
        return result['message'] if result.get('success') else _get_default_fleet_report(total_vessels, average_esg, total_emissions)
    except Exception as e:
        return _get_default_fleet_report(total_vessels, average_esg, total_emissions)


def _get_default_fleet_report(total_vessels: int, average_esg: float, total_emissions: float) -> str:
    """Fallback fleet report when Ollama is unavailable."""
    return f"""# Fleet Environmental Performance Report

## Executive Summary
The fleet consists of {total_vessels} vessels with an average ESG score of {average_esg:.1f}/100 and total emissions of {total_emissions/1000:.2f} tonnes CO₂.

## Recommendations
1. Implement fleet-wide speed optimization programs
2. Conduct regular efficiency audits for underperforming vessels
3. Invest in fuel-efficient technologies and alternative fuels
4. Establish best practice sharing among top performers
5. Develop vessel-specific improvement plans for critical performers

## Action Plan
- **Immediate**: Identify and address critical performers
- **Short-term**: Implement monitoring and reporting systems
- **Long-term**: Transition to cleaner fuels and technologies
"""
