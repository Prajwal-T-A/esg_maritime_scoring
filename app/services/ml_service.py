"""
ML Inference Service

This service handles loading and serving predictions from the trained
RandomForestRegressor model for maritime CO₂ emission estimation.

The model is loaded once at module import (startup) and reused for all
predictions to avoid repeated I/O operations.

Feature Order (must match training):
    1. avg_speed
    2. speed_std
    3. total_distance_km
    4. time_at_sea_hours
    5. acceleration_events
    6. length
    7. width
    8. draft
    9. co2_factor
"""

import joblib
from pathlib import Path
from typing import Dict, Optional
import logging
import pandas as pd
import numpy as np

# Configure logging
logger = logging.getLogger(__name__)

# Path to trained model (relative to project root)
MODEL_PATH = Path(__file__).parent.parent.parent / "ml" / "models" / "emission_model.pkl"

# Global variable to hold the loaded model
_model = None


def load_model():
    """
    Load the trained emission model from disk.
    
    This function is called once at startup to load the model into memory.
    Subsequent predictions reuse the loaded model for efficiency.
    
    Returns
    -------
    model : RandomForestRegressor
        Loaded scikit-learn model
    
    Raises
    ------
    FileNotFoundError
        If the model file doesn't exist
    Exception
        If the model fails to load
    """
    global _model
    
    if _model is not None:
        # Model already loaded
        return _model
    
    try:
        logger.info(f"Loading ML model from {MODEL_PATH}")
        
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Model file not found at {MODEL_PATH}. "
                "Please ensure the model has been trained and saved."
            )
        
        # Use joblib to load the model (compatible with scikit-learn models)
        _model = joblib.load(MODEL_PATH)
        
        logger.info("ML model loaded successfully")
        return _model
    
    except Exception as e:
        logger.error(f"Failed to load ML model: {str(e)}")
        raise


def predict_emissions(features: Dict[str, float]) -> float:
    """
    Predict CO₂ emissions for a vessel based on operational features.
    
    This function takes vessel features as a dictionary and returns the
    predicted baseline CO₂ emissions in kilograms.
    
    Feature extraction handles missing values with safe defaults based on
    fleet averages from the training data.
    
    Parameters
    ----------
    features : dict
        Dictionary containing vessel features:
        - avg_speed: Average speed over ground (knots)
        - speed_std: Standard deviation of speed (knots)
        - total_distance_km: Total distance traveled (km)
        - time_at_sea_hours: Total operational time (hours)
        - acceleration_events: Count of significant speed changes
        - length: Vessel length (meters)
        - width: Vessel width (meters)
        - draft: Vessel draft (meters)
        - co2_factor: CO₂ emission factor (kg CO₂ per fuel unit)
    
    Returns
    -------
    float
        Predicted baseline CO₂ emissions in kilograms
    
    Raises
    ------
    ValueError
        If required features are missing or invalid
    RuntimeError
        If model prediction fails
    
    Examples
    --------
    >>> features = {
    ...     'avg_speed': 12.5,
    ...     'speed_std': 2.1,
    ...     'total_distance_km': 150.0,
    ...     'time_at_sea_hours': 48.0,
    ...     'acceleration_events': 5,
    ...     'length': 200.0,
    ...     'width': 30.0,
    ...     'draft': 10.0,
    ...     'co2_factor': 3.206
    ... }
    >>> predict_emissions(features)
    5432.18
    """
    # Ensure model is loaded
    model = load_model()
    
    try:
        # Extract features in the exact order expected by the model
        # This order MUST match the training feature order
        feature_vector = [
            _extract_feature(features, 'avg_speed', default=10.0, min_val=0.0, max_val=50.0),
            _extract_feature(features, 'speed_std', default=2.0, min_val=0.0, max_val=20.0),
            _extract_feature(features, 'total_distance_km', default=100.0, min_val=0.0),
            _extract_feature(features, 'time_at_sea_hours', default=24.0, min_val=0.0),
            _extract_feature(features, 'acceleration_events', default=10, min_val=0, is_int=True),
            _extract_feature(features, 'length', default=100.0, min_val=0.0, max_val=500.0),
            _extract_feature(features, 'width', default=20.0, min_val=0.0, max_val=100.0),
            _extract_feature(features, 'draft', default=8.0, min_val=0.0, max_val=50.0),
            _extract_feature(features, 'co2_factor', default=3.206, min_val=0.0, max_val=10.0)
        ]
        
        # Log feature vector for debugging (can be disabled in production)
        logger.debug(f"Feature vector: {feature_vector}")
        
        # Make prediction
        # Model expects 2D array: [[features]]
        feature_names = [
            'avg_speed',
            'speed_std',
            'total_distance_km',
            'time_at_sea_hours',
            'acceleration_events',
            'length',
            'width',
            'draft',
            'co2_factor'
        ]

        X = pd.DataFrame([feature_vector], columns=feature_names)
        log_prediction = model.predict(X)[0]
        prediction = np.expm1(log_prediction)
        
        # Ensure prediction is non-negative
        prediction = max(0.0, float(prediction))
        
        logger.debug(f"Predicted CO₂: {prediction:.2f} kg")
        
        return prediction
    
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        raise RuntimeError(f"Failed to predict emissions: {str(e)}")


def _extract_feature(
    features: Dict[str, float],
    key: str,
    default: float,
    min_val: Optional[float] = None,
    max_val: Optional[float] = None,
    is_int: bool = False
) -> float:
    """
    Safely extract and validate a feature from the input dictionary.
    
    This helper function handles:
    - Missing keys (returns default)
    - None values (returns default)
    - Type conversion
    - Range validation
    - Integer conversion if needed
    
    Parameters
    ----------
    features : dict
        Input feature dictionary
    key : str
        Feature key to extract
    default : float
        Default value if missing or invalid
    min_val : float, optional
        Minimum allowed value
    max_val : float, optional
        Maximum allowed value
    is_int : bool
        Whether to convert to integer
    
    Returns
    -------
    float
        Extracted and validated feature value
    """
    try:
        # Get value or use default
        value = features.get(key, default)
        
        # Handle None
        if value is None:
            logger.warning(f"Feature '{key}' is None, using default: {default}")
            return default
        
        # Convert to appropriate type
        if is_int:
            value = int(value)
        else:
            value = float(value)
        
        # Apply range constraints
        if min_val is not None and value < min_val:
            logger.warning(f"Feature '{key}' value {value} below minimum {min_val}, clamping")
            value = min_val
        
        if max_val is not None and value > max_val:
            logger.warning(f"Feature '{key}' value {value} above maximum {max_val}, clamping")
            value = max_val
        
        return value
    
    except (ValueError, TypeError) as e:
        logger.warning(f"Invalid value for '{key}': {features.get(key)}. Using default: {default}. Error: {e}")
        return default


def get_model_info() -> Dict[str, any]:
    """
    Get information about the loaded model.
    
    Returns
    -------
    dict
        Model metadata including type, feature count, and status
    """
    model = load_model()
    
    return {
        "model_type": type(model).__name__,
        "model_path": str(MODEL_PATH),
        "n_features": model.n_features_in_,
        "n_estimators": getattr(model, 'n_estimators', None),
        "max_depth": getattr(model, 'max_depth', None),
        "is_loaded": _model is not None
    }


# Initialize model at module import (startup)
try:
    load_model()
    logger.info("ML service initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize ML service: {str(e)}")
    # Don't crash the entire app if model loading fails
    # Allow the app to start but predictions will fail with clear error messages
