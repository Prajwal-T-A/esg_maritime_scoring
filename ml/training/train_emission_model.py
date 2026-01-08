"""
Emission Model Training Module

This module trains a Random Forest regression model to estimate
vessel CO₂ emissions using AIS-derived features.

Key improvements:
- Log-transform target variable to reduce skew
- Evaluate predictions on original CO₂ scale
- Preserve interpretability for ESG policy integration
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config import AIS_FEATURES_FILE, MODEL_OUTPUT_FILE


def load_features():
    print(f"Loading features from {AIS_FEATURES_FILE}...")
    df = pd.read_csv(AIS_FEATURES_FILE)
    print(f"Loaded {len(df)} vessel records with {df.shape[1]} columns")
    return df


def prepare_training_data(df):
    print("\nPreparing training data...")

    feature_columns = [
        "avg_speed",
        "speed_std",
        "total_distance_km",
        "time_at_sea_hours",
        "acceleration_events",
        "length",
        "width",
        "draft",
        "co2_factor"
    ]

    X = df[feature_columns].copy()

    # Fill missing physical dimensions with median values
    for col in ["length", "width", "draft"]:
        median_val = X[col].median()
        X[col] = X[col].fillna(median_val)
        print(f"  - Filled missing values in {col} with median: {median_val:.2f}")

    # Log-transform target to reduce skew
    y = np.log1p(df["baseline_co2"])

    print(f"\n  - Selected {len(feature_columns)} numeric features:")
    for col in feature_columns:
        print(f"    • {col}")

    print(f"\n  - Final dataset size: {X.shape[0]} samples")
    print(
        f"  - Original target range: "
        f"[{df['baseline_co2'].min():,.2f}, {df['baseline_co2'].max():,.2f}] kg CO₂"
    )

    return X, y


def train_model(X_train, y_train):
    print("\nTraining Random Forest Regressor...")

    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_train, y_train)

    print("Model training complete!")
    return model


def evaluate_model(model, X_train, y_train, X_test, y_test):
    print("\n" + "=" * 60)
    print("MODEL PERFORMANCE EVALUATION")
    print("=" * 60)

    # Predict (log scale)
    y_train_pred_log = model.predict(X_train)
    y_test_pred_log = model.predict(X_test)

    # Convert back to original CO₂ scale
    y_train_pred = np.expm1(y_train_pred_log)
    y_test_pred = np.expm1(y_test_pred_log)

    y_train_true = np.expm1(y_train)
    y_test_true = np.expm1(y_test)

    # Metrics
    train_mse = mean_squared_error(y_train_true, y_train_pred)
    test_mse = mean_squared_error(y_test_true, y_test_pred)

    train_rmse = np.sqrt(train_mse)
    test_rmse = np.sqrt(test_mse)

    train_r2 = r2_score(y_train_true, y_train_pred)
    test_r2 = r2_score(y_test_true, y_test_pred)

    print("\nTraining Set:")
    print(f"  - RMSE: {train_rmse:,.2f} kg CO₂")
    print(f"  - R² Score: {train_r2:.4f}")

    print("\nTest Set:")
    print(f"  - RMSE: {test_rmse:,.2f} kg CO₂")
    print(f"  - R² Score: {test_r2:.4f}")

    if train_r2 - test_r2 > 0.3:
        print("\n⚠ Warning: Possible overfitting detected")
    else:
        print("\n✓ Generalization gap within acceptable range")

    return model


def print_feature_importance(model, feature_names):
    print("\n" + "=" * 60)
    print("FEATURE IMPORTANCE RANKINGS")
    print("=" * 60)

    importances = model.feature_importances_
    importance_df = (
        pd.DataFrame({
            "feature": feature_names,
            "importance": importances
        })
        .sort_values(by="importance", ascending=False)
    )

    for _, row in importance_df.iterrows():
        bar = "█" * int(row["importance"] * 50)
        print(f"{row['feature']:<25} {row['importance']:.4f} {bar}")

    print("\nInterpretation:")
    print("  - Higher importance = greater influence on CO₂ predictions")
    print("  - Dominant features reflect physical emission drivers")


def save_model(model):
    MODEL_OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_OUTPUT_FILE)
    print(f"\nModel saved to {MODEL_OUTPUT_FILE}")
    print(f"  - Model file size: {MODEL_OUTPUT_FILE.stat().st_size / 1024:.2f} KB")


def main():
    print("=" * 60)
    print("EMISSION MODEL TRAINING PIPELINE")
    print("=" * 60)

    df = load_features()
    X, y = prepare_training_data(df)

    print("\nSplitting data into train/test sets...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print(f"  - Training set: {len(X_train)} samples")
    print(f"  - Test set: {len(X_test)} samples")

    model = train_model(X_train, y_train)

    print_feature_importance(model, X.columns)

    evaluate_model(model, X_train, y_train, X_test, y_test)

    save_model(model)

    print("\n" + "=" * 60)
    print("TRAINING COMPLETE")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Add ESG policy scoring layer")
    print("  2. Integrate model into FastAPI backend")


if __name__ == "__main__":
    main()