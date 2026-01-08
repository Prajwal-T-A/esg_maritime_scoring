"""
Feature Engineering Module

This module creates vessel-level features from cleaned AIS data:
- Aggregates vessel behavior metrics (speed, distance, time at sea)
- Computes acceleration events from speed changes
- Normalizes AIS vessel type codes to semantic classes
- Maps vessel types to emission factors
- Calculates baseline CO₂ emissions using physics-based approximations
- Outputs ML-ready feature set for training
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
import warnings

# Silence harmless numpy warnings from AIS edge cases
warnings.filterwarnings("ignore", category=RuntimeWarning)

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from config import (
    AIS_CLEANED_FILE,
    EMISSION_FACTORS_FILE,
    AIS_FEATURES_FILE,
    FEATURES_DATA_DIR,
    ACCELERATION_THRESHOLD
)


# ---------------------------------------------------------
# Vessel type normalization (CRITICAL FIX)
# ---------------------------------------------------------
def normalize_vessel_type(vessel_type):
    """
    Map numeric AIS vessel type codes to semantic vessel classes.

    NOAA / ITU reference:
    - 30–39 → Fishing
    - 60–69 → Passenger
    - 70–79 → Cargo
    - 80–89 → Tanker
    """
    try:
        vt = int(vessel_type)
    except (ValueError, TypeError):
        return "other"

    if 30 <= vt <= 39:
        return "fishing"
    elif 60 <= vt <= 69:
        return "passenger"
    elif 70 <= vt <= 79:
        return "cargo"
    elif 80 <= vt <= 89:
        return "tanker"
    else:
        return "other"


# ---------------------------------------------------------
# Data loaders
# ---------------------------------------------------------
def load_cleaned_ais_data():
    print(f"Loading cleaned AIS data from {AIS_CLEANED_FILE}...")
    df = pd.read_csv(AIS_CLEANED_FILE)
    df["base_date_time"] = pd.to_datetime(df["base_date_time"])
    print(f"Loaded {len(df)} records for {df['mmsi'].nunique()} vessels")
    return df


def load_emission_factors():
    print(f"\nLoading emission factors from {EMISSION_FACTORS_FILE}...")
    df = pd.read_csv(EMISSION_FACTORS_FILE)
    df["vessel_type"] = df["vessel_type"].str.lower()
    print(f"Loaded {len(df)} emission factor records")
    return df


# ---------------------------------------------------------
# Feature aggregation
# ---------------------------------------------------------
def aggregate_vessel_features(df):
    print("\nAggregating vessel-level features...")
    vessel_features = []

    for mmsi, group in df.groupby("mmsi"):
        avg_speed = group["sog"].mean()
        speed_std = group["sog"].std()
        total_distance_km = group["distance_km"].sum()

        if len(group) > 1:
            time_span = (
                group["base_date_time"].max()
                - group["base_date_time"].min()
            ).total_seconds()
            time_at_sea_hours = time_span / 3600.0
        else:
            time_at_sea_hours = 0.0

        speed_diffs = group["sog"].diff().abs()
        acceleration_events = (speed_diffs > ACCELERATION_THRESHOLD).sum()

        vessel_type = (
            group["vessel_type"].mode()[0]
            if not group["vessel_type"].mode().empty
            else group["vessel_type"].iloc[0]
        )

        vessel_features.append({
            "mmsi": mmsi,
            "avg_speed": avg_speed if not pd.isna(avg_speed) else 0.0,
            "speed_std": speed_std if not pd.isna(speed_std) else 0.0,
            "total_distance_km": total_distance_km,
            "time_at_sea_hours": time_at_sea_hours,
            "acceleration_events": acceleration_events,
            "vessel_type": vessel_type,
            "length": group["length"].median(),
            "width": group["width"].median(),
            "draft": group["draft"].median(),
            "cargo": (
                group["cargo"].mode()[0]
                if not group["cargo"].mode().empty
                else group["cargo"].iloc[0]
            )
        })

    features_df = pd.DataFrame(vessel_features)

    print(f"  - Created features for {len(features_df)} vessels")
    print(f"  - Average speed (fleet): {features_df['avg_speed'].mean():.2f} knots")
    print(f"  - Total distance (fleet): {features_df['total_distance_km'].sum():,.2f} km")

    return features_df


# ---------------------------------------------------------
# Emission factor mapping
# ---------------------------------------------------------
def map_emission_factors(features_df, emission_factors_df):
    print("\nMapping emission factors to vessels...")

    # Normalize AIS vessel type codes
    features_df["vessel_type"] = features_df["vessel_type"].apply(normalize_vessel_type)

    emission_map = (
        emission_factors_df
        .groupby("vessel_type")
        .first()
        .reset_index()
    )

    features_df = features_df.merge(
        emission_map[["vessel_type", "co2_factor", "fuel_type"]],
        on="vessel_type",
        how="left"
    )

    matched = features_df["co2_factor"].notna().sum()
    unmatched = features_df["co2_factor"].isna().sum()

    print(f"  - Matched {matched} vessels to emission factors")
    if unmatched > 0:
        print(f"  - Warning: {unmatched} vessels without emission factor mapping")

    return features_df


# ---------------------------------------------------------
# Baseline CO₂ computation
# ---------------------------------------------------------
def compute_baseline_co2(features_df):
    print("\nComputing baseline CO₂ emissions...")

    features_df["fuel_burn_proxy"] = (
        features_df["avg_speed"] * features_df["total_distance_km"]
    )

    median_co2_factor = features_df["co2_factor"].median()
    features_df["co2_factor"] = features_df["co2_factor"].fillna(median_co2_factor)

    features_df["baseline_co2"] = (
        features_df["fuel_burn_proxy"] * features_df["co2_factor"] * 0.1
    )

    print(f"  - Total baseline CO₂: {features_df['baseline_co2'].sum():,.2f} kg")
    print(f"  - Average baseline CO₂ per vessel: {features_df['baseline_co2'].mean():,.2f} kg")
    print(f"  - Min: {features_df['baseline_co2'].min():,.2f} kg")
    print(f"  - Max: {features_df['baseline_co2'].max():,.2f} kg")

    return features_df.drop(columns=["fuel_burn_proxy"])


# ---------------------------------------------------------
# Save output
# ---------------------------------------------------------
def save_features(features_df):
    FEATURES_DATA_DIR.mkdir(parents=True, exist_ok=True)

    print(f"\nSaving features to {AIS_FEATURES_FILE}...")
    features_df.to_csv(AIS_FEATURES_FILE, index=False)
    print(f"Saved {len(features_df)} vessel records")

    print("\nFeature columns:")
    for col in features_df.columns:
        print(f"  - {col}")


# ---------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------
def main():
    print("=" * 60)
    print("FEATURE ENGINEERING PIPELINE")
    print("=" * 60)

    ais_df = load_cleaned_ais_data()
    emission_factors_df = load_emission_factors()

    features_df = aggregate_vessel_features(ais_df)
    features_df = map_emission_factors(features_df, emission_factors_df)
    features_df = compute_baseline_co2(features_df)

    save_features(features_df)

    print("\n" + "=" * 60)
    print("FEATURE ENGINEERING COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()