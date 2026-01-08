"""
Configuration file for ML pipeline.
Centralizes all file paths and constants used across the pipeline.
"""

from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Data directories
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
FEATURES_DATA_DIR = DATA_DIR / "features"

# Model directory
MODELS_DIR = BASE_DIR / "models"

# Raw data files
AIS_RAW_FILE = RAW_DATA_DIR / "ais_raw.csv"
EMISSION_FACTORS_FILE = RAW_DATA_DIR / "emission_factors.csv"

# Processed data files
AIS_CLEANED_FILE = PROCESSED_DATA_DIR / "ais_cleaned.csv"

# Feature files
AIS_FEATURES_FILE = FEATURES_DATA_DIR / "ais_features.csv"

# Model files
EMISSION_MODEL_FILE = MODELS_DIR / "emission_model.pkl"
MODEL_OUTPUT_FILE = BASE_DIR / "models" / "emission_model.pkl"

# Model parameters
RANDOM_SEED = 42
TEST_SIZE = 0.2
N_ESTIMATORS = 100
MAX_DEPTH = 10

# Earth radius for haversine calculation (km)
EARTH_RADIUS_KM = 6371.0

# Speed change threshold for acceleration events (knots)
ACCELERATION_THRESHOLD = 2.0
