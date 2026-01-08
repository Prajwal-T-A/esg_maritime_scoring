"""
AIS Data Preprocessing Module

This module loads raw AIS data, cleans it, and computes derived features:
- Validates and filters invalid location and speed data
- Computes distance traveled between consecutive AIS points using haversine formula
- Computes time differences between AIS transmissions
- Saves cleaned data for downstream feature engineering

The haversine formula calculates the great-circle distance between two points
on a sphere given their longitudes and latitudes.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from config import (
    AIS_RAW_FILE,
    AIS_CLEANED_FILE,
    PROCESSED_DATA_DIR,
    EARTH_RADIUS_KM
)


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points on Earth.
    
    Uses the haversine formula to compute distance in kilometers.
    
    Parameters
    ----------
    lat1, lon1 : float
        Latitude and longitude of first point in decimal degrees
    lat2, lon2 : float
        Latitude and longitude of second point in decimal degrees
    
    Returns
    -------
    float
        Distance in kilometers
    """
    # Convert decimal degrees to radians
    lat1_rad = np.radians(lat1)
    lat2_rad = np.radians(lat2)
    lon1_rad = np.radians(lon1)
    lon2_rad = np.radians(lon2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    
    distance = EARTH_RADIUS_KM * c
    return distance


def load_ais_data():
    """
    Load raw AIS data from CSV file.
    
    Returns
    -------
    pd.DataFrame
        Raw AIS data
    """
    print(f"Loading AIS data from {AIS_RAW_FILE}...")
    df = pd.read_csv(AIS_RAW_FILE)
    print(f"Loaded {len(df)} records")
    return df


def clean_ais_data(df):
    """
    Clean and validate AIS data.
    
    Operations:
    - Parse timestamps
    - Remove invalid coordinates
    - Remove invalid speed values
    - Sort by vessel and time
    
    Parameters
    ----------
    df : pd.DataFrame
        Raw AIS data
    
    Returns
    -------
    pd.DataFrame
        Cleaned AIS data
    """
    print("\nCleaning AIS data...")
    initial_count = len(df)
    
    # Parse datetime
    df['base_date_time'] = pd.to_datetime(df['base_date_time'], errors='coerce')
    print(f"  - Parsed timestamps")
    
    # Remove rows with invalid timestamps
    df = df.dropna(subset=['base_date_time'])
    
    # Remove invalid latitude/longitude (outside valid ranges)
    df = df[(df['latitude'].notna()) & (df['longitude'].notna())]
    df = df[(df['latitude'] >= -90) & (df['latitude'] <= 90)]
    df = df[(df['longitude'] >= -180) & (df['longitude'] <= 180)]
    print(f"  - Removed invalid coordinates")
    
    # Remove rows where speed over ground is null or negative
    df = df[(df['sog'].notna()) & (df['sog'] >= 0)]
    print(f"  - Removed invalid speed values")
    
    # Sort by vessel (mmsi) and time
    df = df.sort_values(['mmsi', 'base_date_time']).reset_index(drop=True)
    print(f"  - Sorted by MMSI and timestamp")
    
    final_count = len(df)
    removed = initial_count - final_count
    print(f"\nRemoved {removed} invalid records ({removed/initial_count*100:.2f}%)")
    print(f"Remaining records: {final_count}")
    
    return df


def compute_derived_features(df):
    """
    Compute distance traveled and time differences between consecutive AIS points.
    
    For each vessel (MMSI), calculates:
    - Distance between consecutive positions (haversine formula)
    - Time difference in seconds between consecutive transmissions
    
    Parameters
    ----------
    df : pd.DataFrame
        Cleaned AIS data sorted by MMSI and timestamp
    
    Returns
    -------
    pd.DataFrame
        AIS data with distance_km and time_diff_seconds columns
    """
    print("\nComputing derived features...")
    
    # Initialize new columns
    df['distance_km'] = 0.0
    df['time_diff_seconds'] = 0.0
    
    # Group by vessel
    for mmsi, group in df.groupby('mmsi'):
        if len(group) < 2:
            continue
            
        indices = group.index
        
        # Calculate distance between consecutive points
        for i in range(1, len(indices)):
            curr_idx = indices[i]
            prev_idx = indices[i-1]
            
            # Haversine distance
            distance = haversine_distance(
                df.loc[prev_idx, 'latitude'],
                df.loc[prev_idx, 'longitude'],
                df.loc[curr_idx, 'latitude'],
                df.loc[curr_idx, 'longitude']
            )
            df.loc[curr_idx, 'distance_km'] = distance
            
            # Time difference in seconds
            time_diff = (df.loc[curr_idx, 'base_date_time'] - 
                        df.loc[prev_idx, 'base_date_time']).total_seconds()
            df.loc[curr_idx, 'time_diff_seconds'] = time_diff
    
    # Summary statistics
    total_distance = df['distance_km'].sum()
    avg_distance = df[df['distance_km'] > 0]['distance_km'].mean()
    
    print(f"  - Total distance traveled: {total_distance:,.2f} km")
    print(f"  - Average distance per transmission: {avg_distance:.4f} km")
    print(f"  - Computed for {df['mmsi'].nunique()} unique vessels")
    
    return df


def save_cleaned_data(df):
    """
    Save cleaned AIS data to CSV file.
    
    Parameters
    ----------
    df : pd.DataFrame
        Cleaned AIS data with derived features
    """
    # Ensure output directory exists
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"\nSaving cleaned data to {AIS_CLEANED_FILE}...")
    df.to_csv(AIS_CLEANED_FILE, index=False)
    print(f"Saved {len(df)} records")


def main():
    """
    Main preprocessing pipeline.
    
    Orchestrates:
    1. Loading raw AIS data
    2. Cleaning and validation
    3. Computing derived features (distance, time)
    4. Saving processed data
    """
    print("="*60)
    print("AIS DATA PREPROCESSING PIPELINE")
    print("="*60)
    
    # Load raw data
    df = load_ais_data()
    
    # Clean data
    df = clean_ais_data(df)
    
    # Compute derived features
    df = compute_derived_features(df)
    
    # Save cleaned data
    save_cleaned_data(df)
    
    print("\n" + "="*60)
    print("PREPROCESSING COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main()
