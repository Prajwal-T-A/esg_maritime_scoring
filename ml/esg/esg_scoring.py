"""
ESG Environmental Scoring Module

This module computes an environmental ESG score for maritime vessels based on:
- CO₂ emission intensity (emissions per kilometer traveled)
- Operational behavior (acceleration patterns, speed, duration)

The scoring system is designed to be:
- Deterministic: Same inputs always produce same outputs
- Explainable: Clear penalties with policy reasoning
- Actionable: Risk flags identify specific improvement areas

Score Range: 0-100 (higher is better)
- 90-100: Excellent environmental performance
- 70-89:  Good environmental performance
- 50-69:  Moderate environmental performance
- 30-49:  Poor environmental performance
- 0-29:   Critical environmental performance
"""

from typing import Dict, List, Tuple


# ============================================================================
# ESG SCORING THRESHOLDS
# ============================================================================
# These thresholds are based on maritime environmental best practices and
# can be adjusted based on regulatory requirements or fleet benchmarks

# CO₂ Intensity Threshold (kg CO₂ per km)
# Policy reasoning: Vessels exceeding this threshold are significantly more
# carbon-intensive than efficient vessels in their class
CO2_INTENSITY_THRESHOLD = 50.0  # kg CO₂/km

# Acceleration Events Threshold
# Policy reasoning: Frequent speed changes indicate inefficient operations,
# leading to higher fuel consumption and emissions. Smooth operations are
# preferred for both environmental and safety reasons.
ACCELERATION_EVENTS_THRESHOLD = 15  # count

# Average Speed Limit (knots)
# Policy reasoning: Excessive speed increases fuel consumption exponentially
# (fuel consumption ∝ speed³). Optimal cruising speed balances efficiency
# and operational requirements.
AVG_SPEED_LIMIT = 10.0  # knots

# Long Duration Threshold (hours)
# Policy reasoning: Extended continuous operations without port stops may
# indicate inefficient routing or lack of optimization. However, this is
# context-dependent (e.g., transoceanic routes vs. coastal shipping).
LONG_DURATION_THRESHOLD = 720.0  # hours (30 days)

# Penalty values (subtracted from base score of 100)
PENALTY_HIGH_CO2_INTENSITY = 25  # Largest penalty - direct emissions impact
PENALTY_HIGH_ACCELERATION = 15   # Medium penalty - operational inefficiency
PENALTY_HIGH_SPEED = 10          # Lower penalty - efficiency concern
PENALTY_LONG_DURATION = 10       # Lower penalty - route optimization concern


# ============================================================================
# CORE ESG SCORING FUNCTION
# ============================================================================

def compute_esg_score(
    baseline_co2: float,
    total_distance_km: float,
    avg_speed: float,
    acceleration_events: int,
    time_at_sea_hours: float
) -> Tuple[int, List[str]]:
    """
    Compute environmental ESG score for a vessel based on operational metrics.
    
    The scoring system starts with a perfect score of 100 and applies penalties
    for environmental and operational inefficiencies. Each penalty represents
    a specific area where the vessel can improve its environmental performance.
    
    Parameters
    ----------
    baseline_co2 : float
        Total CO₂ emissions in kilograms
    total_distance_km : float
        Total distance traveled in kilometers
    avg_speed : float
        Average speed over ground in knots
    acceleration_events : int
        Count of significant speed change events
    time_at_sea_hours : float
        Total operational time in hours
    
    Returns
    -------
    tuple
        (esg_score, risk_flags) where:
        - esg_score (int): Environmental score from 0-100
        - risk_flags (list): List of triggered environmental risk indicators
    
    Examples
    --------
    >>> compute_esg_score(5000.0, 100.0, 12.0, 5, 48.0)
    (90, [])  # Good performance, no risk flags
    
    >>> compute_esg_score(10000.0, 100.0, 20.0, 30, 800.0)
    (40, ['High CO2 intensity', 'Excessive acceleration', 'High speed', 'Extended duration'])
    """
    # Initialize scoring
    score = 100
    risk_flags = []
    
    # ========================================================================
    # PENALTY 1: CO₂ EMISSION INTENSITY
    # ========================================================================
    # CO₂ intensity (emissions per distance) is the primary environmental metric
    # It normalizes emissions by distance traveled, allowing fair comparison
    # between vessels with different operational profiles
    
    if total_distance_km > 0:
        co2_intensity = baseline_co2 / total_distance_km
    else:
        # Handle edge case: no distance traveled
        # If vessel emitted CO₂ but didn't move, assign maximum intensity
        co2_intensity = float('inf') if baseline_co2 > 0 else 0.0
    
    if co2_intensity > CO2_INTENSITY_THRESHOLD:
        score -= PENALTY_HIGH_CO2_INTENSITY
        risk_flags.append(
            f"High CO2 intensity ({co2_intensity:.2f} kg/km > "
            f"{CO2_INTENSITY_THRESHOLD} kg/km threshold)"
        )
        # Policy note: High CO₂ intensity indicates:
        # - Inefficient engine operation
        # - Suboptimal speed profile
        # - Potential need for engine maintenance or upgrade
        # - Possible use of high-carbon fuel
    
    # ========================================================================
    # PENALTY 2: EXCESSIVE ACCELERATION EVENTS
    # ========================================================================
    # Frequent speed changes indicate operational inefficiency
    # Smooth, consistent operations reduce fuel consumption and emissions
    
    if acceleration_events > ACCELERATION_EVENTS_THRESHOLD:
        score -= PENALTY_HIGH_ACCELERATION
        risk_flags.append(
            f"Excessive acceleration events ({acceleration_events} > "
            f"{ACCELERATION_EVENTS_THRESHOLD} threshold)"
        )
        # Policy note: High acceleration events suggest:
        # - Poor voyage planning
        # - Inefficient navigation in congested waters
        # - Suboptimal autopilot settings
        # - Potential safety concerns in maneuvering
    
    # ========================================================================
    # PENALTY 3: HIGH AVERAGE SPEED
    # ========================================================================
    # Speed has exponential relationship with fuel consumption and emissions
    # Slow steaming (reduced speed) is a proven emission reduction strategy
    
    if avg_speed > AVG_SPEED_LIMIT:
        score -= PENALTY_HIGH_SPEED
        risk_flags.append(
            f"High average speed ({avg_speed:.2f} knots > "
            f"{AVG_SPEED_LIMIT} knots threshold)"
        )
        # Policy note: High speed operation indicates:
        # - Non-optimal cruising speed (fuel consumption ∝ speed³)
        # - Potential schedule pressure over efficiency
        # - Opportunity for slow steaming implementation
        # - Higher underwater noise pollution
    
    # ========================================================================
    # PENALTY 4: EXTENDED CONTINUOUS OPERATION
    # ========================================================================
    # Very long operational periods may indicate route inefficiency
    # Context-dependent: legitimate for long transoceanic voyages
    
    if time_at_sea_hours > LONG_DURATION_THRESHOLD:
        score -= PENALTY_LONG_DURATION
        risk_flags.append(
            f"Extended operational duration ({time_at_sea_hours:.2f} hours > "
            f"{LONG_DURATION_THRESHOLD} hours threshold)"
        )
        # Policy note: Extended duration may indicate:
        # - Suboptimal route planning
        # - Inefficient port scheduling
        # - However: legitimate for long-haul shipping routes
        # - Consider route optimization and just-in-time arrival
    
    # ========================================================================
    # SCORE BOUNDS AND VALIDATION
    # ========================================================================
    # Ensure score remains within valid range [0, 100]
    # This handles cases where multiple penalties accumulate
    
    if score < 0:
        score = 0
    elif score > 100:
        score = 100
    
    # Return integer score for consistency (ESG scores typically discrete)
    return int(score), risk_flags


def get_score_interpretation(esg_score: int) -> Dict[str, str]:
    """
    Provide human-readable interpretation of ESG score.
    
    Parameters
    ----------
    esg_score : int
        ESG environmental score (0-100)
    
    Returns
    -------
    dict
        Dictionary with rating, description, and recommendations
    
    Examples
    --------
    >>> get_score_interpretation(85)
    {
        'rating': 'Good',
        'description': 'Good environmental performance',
        'recommendation': 'Maintain current practices, minor optimizations possible'
    }
    """
    if esg_score >= 90:
        return {
            'rating': 'Excellent',
            'description': 'Excellent environmental performance',
            'recommendation': 'Industry-leading practices. Share best practices with fleet.',
            'color': 'green'
        }
    elif esg_score >= 70:
        return {
            'rating': 'Good',
            'description': 'Good environmental performance',
            'recommendation': 'Maintain current practices, minor optimizations possible.',
            'color': 'lightgreen'
        }
    elif esg_score >= 50:
        return {
            'rating': 'Moderate',
            'description': 'Moderate environmental performance',
            'recommendation': 'Review operational practices. Focus on reducing identified risks.',
            'color': 'yellow'
        }
    elif esg_score >= 30:
        return {
            'rating': 'Poor',
            'description': 'Poor environmental performance',
            'recommendation': 'Immediate action required. Address all risk flags systematically.',
            'color': 'orange'
        }
    else:
        return {
            'rating': 'Critical',
            'description': 'Critical environmental performance',
            'recommendation': 'Urgent intervention needed. Comprehensive environmental audit recommended.',
            'color': 'red'
        }


def compute_fleet_esg_summary(vessel_scores: List[Tuple[str, int, List[str]]]) -> Dict:
    """
    Compute aggregate ESG metrics for a fleet of vessels.
    
    Parameters
    ----------
    vessel_scores : list of tuples
        List of (vessel_id, esg_score, risk_flags) for each vessel
    
    Returns
    -------
    dict
        Fleet-level ESG statistics including average, distribution, and common risks
    
    Examples
    --------
    >>> fleet_data = [
    ...     ('VESSEL001', 85, []),
    ...     ('VESSEL002', 65, ['High CO2 intensity']),
    ...     ('VESSEL003', 90, [])
    ... ]
    >>> compute_fleet_esg_summary(fleet_data)
    {
        'fleet_average_score': 80.0,
        'total_vessels': 3,
        'excellent_count': 1,
        'good_count': 1,
        'moderate_count': 1,
        'poor_count': 0,
        'critical_count': 0,
        'most_common_risks': ['High CO2 intensity']
    }
    """
    if not vessel_scores:
        return {
            'fleet_average_score': 0,
            'total_vessels': 0,
            'excellent_count': 0,
            'good_count': 0,
            'moderate_count': 0,
            'poor_count': 0,
            'critical_count': 0,
            'most_common_risks': []
        }
    
    # Extract scores and risk flags
    scores = [score for _, score, _ in vessel_scores]
    all_risk_flags = [flag for _, _, flags in vessel_scores for flag in flags]
    
    # Compute distribution
    excellent_count = sum(1 for s in scores if s >= 90)
    good_count = sum(1 for s in scores if 70 <= s < 90)
    moderate_count = sum(1 for s in scores if 50 <= s < 70)
    poor_count = sum(1 for s in scores if 30 <= s < 50)
    critical_count = sum(1 for s in scores if s < 30)
    
    # Find most common risk flags
    from collections import Counter
    risk_counter = Counter(all_risk_flags)
    most_common_risks = [risk for risk, _ in risk_counter.most_common(5)]
    
    return {
        'fleet_average_score': round(sum(scores) / len(scores), 2),
        'total_vessels': len(vessel_scores),
        'excellent_count': excellent_count,
        'good_count': good_count,
        'moderate_count': moderate_count,
        'poor_count': poor_count,
        'critical_count': critical_count,
        'most_common_risks': most_common_risks,
        'vessels_with_risks': sum(1 for _, _, flags in vessel_scores if flags),
        'risk_free_vessels': sum(1 for _, _, flags in vessel_scores if not flags)
    }


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def update_thresholds(
    co2_intensity: float = None,
    acceleration_events: int = None,
    avg_speed: float = None,
    long_duration: float = None
) -> Dict[str, float]:
    """
    Update ESG scoring thresholds (for calibration or regulatory changes).
    
    This function is provided for flexibility but should be used with caution.
    Threshold changes affect score comparability over time.
    
    Parameters
    ----------
    co2_intensity : float, optional
        New CO₂ intensity threshold (kg/km)
    acceleration_events : int, optional
        New acceleration events threshold
    avg_speed : float, optional
        New average speed threshold (knots)
    long_duration : float, optional
        New duration threshold (hours)
    
    Returns
    -------
    dict
        Current threshold values after update
    
    Note
    ----
    For production use, thresholds should be managed through configuration
    files and version controlled to ensure score reproducibility.
    """
    global CO2_INTENSITY_THRESHOLD, ACCELERATION_EVENTS_THRESHOLD
    global AVG_SPEED_LIMIT, LONG_DURATION_THRESHOLD
    
    if co2_intensity is not None:
        CO2_INTENSITY_THRESHOLD = co2_intensity
    if acceleration_events is not None:
        ACCELERATION_EVENTS_THRESHOLD = acceleration_events
    if avg_speed is not None:
        AVG_SPEED_LIMIT = avg_speed
    if long_duration is not None:
        LONG_DURATION_THRESHOLD = long_duration
    
    return get_current_thresholds()


def get_current_thresholds() -> Dict[str, float]:
    """
    Get current ESG scoring thresholds.
    
    Returns
    -------
    dict
        Current threshold values and penalties
    """
    return {
        'co2_intensity_threshold': CO2_INTENSITY_THRESHOLD,
        'acceleration_events_threshold': ACCELERATION_EVENTS_THRESHOLD,
        'avg_speed_limit': AVG_SPEED_LIMIT,
        'long_duration_threshold': LONG_DURATION_THRESHOLD,
        'penalty_high_co2': PENALTY_HIGH_CO2_INTENSITY,
        'penalty_acceleration': PENALTY_HIGH_ACCELERATION,
        'penalty_speed': PENALTY_HIGH_SPEED,
        'penalty_duration': PENALTY_LONG_DURATION
    }


# ============================================================================
# EXAMPLE USAGE AND TESTING
# ============================================================================

if __name__ == "__main__":
    # Example 1: Excellent performance vessel
    print("=" * 70)
    print("EXAMPLE 1: Excellent Environmental Performance")
    print("=" * 70)
    score, flags = compute_esg_score(
        baseline_co2=3000.0,      # Low emissions
        total_distance_km=100.0,   # Moderate distance
        avg_speed=12.0,            # Slow steaming
        acceleration_events=5,     # Smooth operation
        time_at_sea_hours=48.0     # Short voyage
    )
    interpretation = get_score_interpretation(score)
    print(f"ESG Score: {score}/100")
    print(f"Rating: {interpretation['rating']}")
    print(f"Risk Flags: {flags if flags else 'None'}")
    print(f"Recommendation: {interpretation['recommendation']}\n")
    
    # Example 2: Poor performance vessel
    print("=" * 70)
    print("EXAMPLE 2: Poor Environmental Performance")
    print("=" * 70)
    score, flags = compute_esg_score(
        baseline_co2=10000.0,      # High emissions
        total_distance_km=100.0,   # Same distance
        avg_speed=22.0,            # High speed
        acceleration_events=35,    # Erratic operation
        time_at_sea_hours=800.0    # Very long voyage
    )
    interpretation = get_score_interpretation(score)
    print(f"ESG Score: {score}/100")
    print(f"Rating: {interpretation['rating']}")
    print(f"Risk Flags:")
    for flag in flags:
        print(f"  - {flag}")
    print(f"Recommendation: {interpretation['recommendation']}\n")
    
    # Example 3: Fleet summary
    print("=" * 70)
    print("EXAMPLE 3: Fleet-Level ESG Summary")
    print("=" * 70)
    fleet_data = [
        ('VESSEL_001', 95, []),
        ('VESSEL_002', 85, []),
        ('VESSEL_003', 65, ['High CO2 intensity']),
        ('VESSEL_004', 45, ['High CO2 intensity', 'Excessive acceleration']),
        ('VESSEL_005', 90, [])
    ]
    summary = compute_fleet_esg_summary(fleet_data)
    print(f"Fleet Average Score: {summary['fleet_average_score']}/100")
    print(f"Total Vessels: {summary['total_vessels']}")
    print(f"Distribution:")
    print(f"  - Excellent (90-100): {summary['excellent_count']}")
    print(f"  - Good (70-89): {summary['good_count']}")
    print(f"  - Moderate (50-69): {summary['moderate_count']}")
    print(f"  - Poor (30-49): {summary['poor_count']}")
    print(f"  - Critical (0-29): {summary['critical_count']}")
    print(f"Most Common Risks: {summary['most_common_risks']}")
    
    # Display current thresholds
    print("\n" + "=" * 70)
    print("CURRENT ESG SCORING THRESHOLDS")
    print("=" * 70)
    thresholds = get_current_thresholds()
    for key, value in thresholds.items():
        print(f"{key}: {value}")
