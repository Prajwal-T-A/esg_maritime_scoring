"""
ESG Scoring Integration Example

Demonstrates how to integrate ESG scoring with the trained emission model
to provide comprehensive environmental assessments for vessels.
"""

import sys
from pathlib import Path
import pandas as pd
import pickle

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from config import AIS_FEATURES_FILE, EMISSION_MODEL_FILE
from esg.esg_scoring import (
    compute_esg_score, 
    get_score_interpretation,
    compute_fleet_esg_summary
)


def score_vessels_from_features(features_file=AIS_FEATURES_FILE):
    """
    Load vessel features and compute ESG scores for all vessels.
    
    Parameters
    ----------
    features_file : Path or str
        Path to the vessel features CSV file
    
    Returns
    -------
    pd.DataFrame
        DataFrame with vessel features and ESG scores
    """
    print("="*70)
    print("ESG SCORING - VESSEL FLEET ASSESSMENT")
    print("="*70)
    
    # Load vessel features
    print(f"\nLoading vessel features from {features_file}...")
    df = pd.read_csv(features_file)
    print(f"Loaded {len(df)} vessels")
    df = df[df["total_distance_km"] >= 10.0]
    # Compute ESG scores for each vessel
    print("\nComputing ESG scores...")
    esg_scores = []
    risk_flags_list = []
 
    for idx, row in df.iterrows():
        score, flags = compute_esg_score(
            baseline_co2=row['baseline_co2'],
            total_distance_km=row['total_distance_km'],
            avg_speed=row['avg_speed'],
            acceleration_events=int(row['acceleration_events']),
            time_at_sea_hours=row['time_at_sea_hours']
        )
        esg_scores.append(score)
        risk_flags_list.append(flags)
    
    # Add scores to dataframe
    df['esg_score'] = esg_scores
    df['risk_flags'] = risk_flags_list
    df['risk_count'] = [len(flags) for flags in risk_flags_list]
    
    # Add interpretation
    interpretations = [get_score_interpretation(score) for score in esg_scores]
    df['esg_rating'] = [interp['rating'] for interp in interpretations]
    
    return df


def display_top_bottom_performers(df, n=5):
    """
    Display top and bottom performing vessels by ESG score.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with ESG scores
    n : int
        Number of top/bottom vessels to display
    """
    print("\n" + "="*70)
    print(f"TOP {n} ENVIRONMENTAL PERFORMERS")
    print("="*70)
    
    top_performers = df.nlargest(n, 'esg_score')
    for idx, row in top_performers.iterrows():
        # Calculate CO₂ intensity safely
        co2_intensity = row['baseline_co2'] / row['total_distance_km'] if row['total_distance_km'] > 0 else 0.0
        
        print(f"\nMMSI: {row['mmsi']}")
        print(f"  ESG Score: {row['esg_score']}/100 ({row['esg_rating']})")
        print(f"  CO₂ Emissions: {row['baseline_co2']:,.2f} kg")
        print(f"  Distance: {row['total_distance_km']:,.2f} km")
        print(f"  CO₂ Intensity: {co2_intensity:.2f} kg/km")
        print(f"  Risk Flags: {row['risk_count']}")
    
    print("\n" + "="*70)
    print(f"BOTTOM {n} ENVIRONMENTAL PERFORMERS (Needs Improvement)")
    print("="*70)
    
    bottom_performers = df.nsmallest(n, 'esg_score')
    for idx, row in bottom_performers.iterrows():
        # Calculate CO₂ intensity safely
        co2_intensity = row['baseline_co2'] / row['total_distance_km'] if row['total_distance_km'] > 0 else 0.0
        
        print(f"\nMMSI: {row['mmsi']}")
        print(f"  ESG Score: {row['esg_score']}/100 ({row['esg_rating']})")
        print(f"  CO₂ Emissions: {row['baseline_co2']:,.2f} kg")
        print(f"  Distance: {row['total_distance_km']:,.2f} km")
        print(f"  CO₂ Intensity: {co2_intensity:.2f} kg/km")
        print(f"  Risk Flags ({row['risk_count']}):")
        for flag in row['risk_flags']:
            print(f"    - {flag}")


def display_fleet_summary(df):
    """
    Display fleet-level ESG summary statistics.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with ESG scores
    """
    # Prepare data for fleet summary
    vessel_scores = [
        (str(row['mmsi']), row['esg_score'], row['risk_flags'])
        for _, row in df.iterrows()
    ]
    
    summary = compute_fleet_esg_summary(vessel_scores)
    
    print("\n" + "="*70)
    print("FLEET-LEVEL ESG SUMMARY")
    print("="*70)
    
    print(f"\nFleet Average Score: {summary['fleet_average_score']}/100")
    print(f"Total Vessels: {summary['total_vessels']}")
    
    print(f"\nPerformance Distribution:")
    print(f"  ⭐ Excellent (90-100): {summary['excellent_count']} vessels "
          f"({summary['excellent_count']/summary['total_vessels']*100:.1f}%)")
    print(f"  ✓  Good (70-89):      {summary['good_count']} vessels "
          f"({summary['good_count']/summary['total_vessels']*100:.1f}%)")
    print(f"  ○  Moderate (50-69):  {summary['moderate_count']} vessels "
          f"({summary['moderate_count']/summary['total_vessels']*100:.1f}%)")
    print(f"  ⚠  Poor (30-49):      {summary['poor_count']} vessels "
          f"({summary['poor_count']/summary['total_vessels']*100:.1f}%)")
    print(f"  ❌ Critical (0-29):   {summary['critical_count']} vessels "
          f"({summary['critical_count']/summary['total_vessels']*100:.1f}%)")
    
    print(f"\nRisk Analysis:")
    print(f"  Vessels with Risk Flags: {summary['vessels_with_risks']} "
          f"({summary['vessels_with_risks']/summary['total_vessels']*100:.1f}%)")
    print(f"  Risk-Free Vessels: {summary['risk_free_vessels']} "
          f"({summary['risk_free_vessels']/summary['total_vessels']*100:.1f}%)")
    
    if summary['most_common_risks']:
        print(f"\nMost Common Risk Flags:")
        for i, risk in enumerate(summary['most_common_risks'], 1):
            print(f"  {i}. {risk}")


def save_esg_results(df, output_file='ml/data/features/vessel_esg_scores.csv'):
    """
    Save ESG scoring results to CSV.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with ESG scores
    output_file : str
        Output file path
    """
    # Prepare output (convert list columns to strings for CSV)
    output_df = df.copy()
    output_df['risk_flags'] = output_df['risk_flags'].apply(lambda x: '; '.join(x) if x else 'None')
    
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    output_df.to_csv(output_path, index=False)
    print(f"\n✓ ESG results saved to {output_path}")


def main():
    """
    Main function to run ESG scoring on vessel fleet.
    """
    # Score all vessels
    df = score_vessels_from_features()
    
    # Display summary statistics
    display_fleet_summary(df)
    
    # Display top and bottom performers
    display_top_bottom_performers(df, n=5)
    
    # Save results
    save_esg_results(df)
    
    print("\n" + "="*70)
    print("ESG SCORING COMPLETE")
    print("="*70)
    print("\nNext steps:")
    print("  1. Review risk flags for poor performers")
    print("  2. Share best practices from top performers")
    print("  3. Develop action plans for vessels with multiple risk flags")
    print("  4. Monitor ESG scores over time to track improvements")


if __name__ == "__main__":
    main()
