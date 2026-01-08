"""
Model Evaluation Module

This module performs comprehensive evaluation of the trained emission model:
- Loads the trained Random Forest model
- Evaluates on test dataset
- Computes and explains performance metrics (RMSE, R²)
- Provides interpretable results for research validation

Metrics explained:
- RMSE (Root Mean Squared Error): Average prediction error in kg CO₂
  Lower is better. Represents typical error magnitude.
  
- R² Score (Coefficient of Determination): Proportion of variance explained
  Range: 0 to 1 (higher is better)
  R² = 1.0: Perfect predictions
  R² = 0.0: Model no better than mean baseline
  R² < 0.0: Model worse than predicting mean
"""

import pandas as pd
import numpy as np
from pathlib import Path
import pickle
import sys

from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.model_selection import train_test_split

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from config import (
    AIS_FEATURES_FILE,
    EMISSION_MODEL_FILE,
    RANDOM_SEED,
    TEST_SIZE
)


def load_model():
    """
    Load trained emission model from disk.
    
    Returns
    -------
    RandomForestRegressor
        Trained model
    """
    print(f"Loading model from {EMISSION_MODEL_FILE}...")
    with open(EMISSION_MODEL_FILE, 'rb') as f:
        model = pickle.load(f)
    print("Model loaded successfully!")
    return model


def load_and_prepare_data():
    """
    Load feature data and prepare for evaluation.
    
    Uses same preprocessing as training to ensure consistency.
    Splits data using same random seed to get identical test set.
    
    Returns
    -------
    tuple
        (X_test, y_test, feature_names)
    """
    print(f"\nLoading features from {AIS_FEATURES_FILE}...")
    df = pd.read_csv(AIS_FEATURES_FILE)
    print(f"Loaded {len(df)} vessel records")
    
    # Define target variable
    target = 'baseline_co2'
    
    # Exclude non-numeric and identifier columns (same as training)
    exclude_cols = ['mmsi', 'vessel_type', 'fuel_type', 'cargo', target]
    
    # Select numeric features
    feature_cols = [col for col in df.columns if col not in exclude_cols]
    numeric_features = []
    for col in feature_cols:
        if pd.api.types.is_numeric_dtype(df[col]):
            numeric_features.append(col)
    
    # Extract features and target
    X = df[numeric_features].values
    y = df[target].values
    
    # Handle missing values (fill with median)
    for i, col in enumerate(numeric_features):
        if np.isnan(X[:, i]).any():
            median_val = np.nanmedian(X[:, i])
            X[:, i] = np.where(np.isnan(X[:, i]), median_val, X[:, i])
    
    # Remove any rows where target is NaN
    valid_indices = ~np.isnan(y)
    X = X[valid_indices]
    y = y[valid_indices]
    
    # Split data (same as training)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=TEST_SIZE, 
        random_state=RANDOM_SEED
    )
    
    print(f"  - Test set size: {len(X_test)} samples")
    
    return X_test, y_test, numeric_features


def compute_metrics(y_true, y_pred):
    """
    Compute comprehensive evaluation metrics.
    
    Parameters
    ----------
    y_true : np.ndarray
        True target values
    y_pred : np.ndarray
        Predicted target values
    
    Returns
    -------
    dict
        Dictionary of metric names and values
    """
    metrics = {
        'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
        'mae': mean_absolute_error(y_true, y_pred),
        'r2': r2_score(y_true, y_pred),
        'mean_true': np.mean(y_true),
        'std_true': np.std(y_true),
        'mean_pred': np.mean(y_pred),
        'std_pred': np.std(y_pred)
    }
    return metrics


def display_evaluation_results(metrics):
    """
    Display evaluation metrics with clear explanations.
    
    Parameters
    ----------
    metrics : dict
        Dictionary of computed metrics
    """
    print("\n" + "="*60)
    print("MODEL EVALUATION RESULTS")
    print("="*60)
    
    print("\n📊 PRIMARY METRICS")
    print("-" * 60)
    
    # RMSE
    print(f"\n✓ RMSE (Root Mean Squared Error)")
    print(f"  Value: {metrics['rmse']:,.2f} kg CO₂")
    print(f"  Interpretation: On average, predictions are off by ~{metrics['rmse']:,.0f} kg")
    print(f"  Relative error: {metrics['rmse']/metrics['mean_true']*100:.1f}% of mean emissions")
    
    # R² Score
    print(f"\n✓ R² Score (Coefficient of Determination)")
    print(f"  Value: {metrics['r2']:.4f}")
    print(f"  Interpretation: Model explains {metrics['r2']*100:.2f}% of variance in emissions")
    
    if metrics['r2'] >= 0.9:
        quality = "Excellent"
    elif metrics['r2'] >= 0.7:
        quality = "Good"
    elif metrics['r2'] >= 0.5:
        quality = "Moderate"
    else:
        quality = "Poor"
    print(f"  Model quality: {quality}")
    
    # MAE
    print(f"\n✓ MAE (Mean Absolute Error)")
    print(f"  Value: {metrics['mae']:,.2f} kg CO₂")
    print(f"  Interpretation: Typical absolute error magnitude")
    
    print("\n" + "-" * 60)
    print("\n📈 TARGET DISTRIBUTION")
    print("-" * 60)
    
    print(f"\nActual emissions (test set):")
    print(f"  Mean: {metrics['mean_true']:,.2f} kg CO₂")
    print(f"  Std:  {metrics['std_true']:,.2f} kg CO₂")
    
    print(f"\nPredicted emissions (test set):")
    print(f"  Mean: {metrics['mean_pred']:,.2f} kg CO₂")
    print(f"  Std:  {metrics['std_pred']:,.2f} kg CO₂")
    
    print("\n" + "-" * 60)
    print("\n📋 METRIC DEFINITIONS")
    print("-" * 60)
    
    print("""
RMSE (Root Mean Squared Error):
  • Measures average prediction error in original units (kg CO₂)
  • Penalizes large errors more heavily than small ones
  • Lower values indicate better performance
  • Same units as target variable for easy interpretation

R² Score (Coefficient of Determination):
  • Proportion of variance in target explained by model
  • Range: (-∞, 1.0], where 1.0 is perfect prediction
  • R² = 1.0: Model perfectly predicts all values
  • R² = 0.0: Model no better than predicting mean
  • R² < 0.0: Model worse than mean baseline
  • Industry standard for regression model quality

MAE (Mean Absolute Error):
  • Average of absolute differences between predictions and actuals
  • Less sensitive to outliers than RMSE
  • Provides linear penalty for all errors
    """)
    
    print("="*60)


def display_prediction_examples(model, X_test, y_test, n_examples=10):
    """
    Display sample predictions vs actual values.
    
    Parameters
    ----------
    model : RandomForestRegressor
        Trained model
    X_test : np.ndarray
        Test features
    y_test : np.ndarray
        Test targets
    n_examples : int
        Number of examples to display
    """
    print("\n" + "="*60)
    print("SAMPLE PREDICTIONS")
    print("="*60)
    
    # Get predictions
    y_pred = model.predict(X_test)
    
    # Calculate errors
    errors = y_pred - y_test
    abs_errors = np.abs(errors)
    percent_errors = (abs_errors / y_test) * 100
    
    # Sample random indices
    np.random.seed(RANDOM_SEED)
    sample_indices = np.random.choice(len(X_test), min(n_examples, len(X_test)), replace=False)
    
    print(f"\nShowing {len(sample_indices)} random predictions:\n")
    print(f"{'#':<4} {'Actual (kg)':<15} {'Predicted (kg)':<15} {'Error (kg)':<15} {'Error %':<10}")
    print("-" * 70)
    
    for i, idx in enumerate(sample_indices, 1):
        print(f"{i:<4} {y_test[idx]:<15,.2f} {y_pred[idx]:<15,.2f} "
              f"{errors[idx]:<15,.2f} {percent_errors[idx]:<10.1f}%")
    
    print("\n" + "="*60)


def main():
    """
    Main evaluation pipeline.
    
    Orchestrates:
    1. Loading trained model
    2. Loading and preparing test data
    3. Making predictions
    4. Computing evaluation metrics
    5. Displaying results with explanations
    6. Showing sample predictions
    """
    print("="*60)
    print("EMISSION MODEL EVALUATION PIPELINE")
    print("="*60)
    
    # Load model
    model = load_model()
    
    # Load test data
    X_test, y_test, feature_names = load_and_prepare_data()
    
    # Make predictions
    print("\nGenerating predictions on test set...")
    y_pred = model.predict(X_test)
    print(f"Generated {len(y_pred)} predictions")
    
    # Compute metrics
    print("\nComputing evaluation metrics...")
    metrics = compute_metrics(y_test, y_pred)
    
    # Display results
    display_evaluation_results(metrics)
    
    # Show sample predictions
    display_prediction_examples(model, X_test, y_test, n_examples=10)
    
    print("\n" + "="*60)
    print("EVALUATION COMPLETE")
    print("="*60)
    
    print("\n✓ Model ready for deployment")
    print("✓ Can be integrated into FastAPI backend for real-time inference")
    print("✓ Use for ESG environmental scoring based on emission predictions")


if __name__ == "__main__":
    main()
