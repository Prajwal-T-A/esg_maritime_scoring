"""
Full ML Pipeline Runner

Executes the complete machine learning pipeline:
1. Data preprocessing
2. Feature engineering
3. Model training
4. Model evaluation

Run this script to execute all pipeline steps sequentially.
"""

import sys
from pathlib import Path

# Add ml directory to path
sys.path.append(str(Path(__file__).parent))

from preprocessing.preprocess_ais import main as preprocess
from features.feature_engineering import main as engineer_features
from training.train_emission_model import main as train_model
from evaluation.evaluate_model import main as evaluate_model


def main():
    """
    Execute full ML pipeline.
    
    Runs all stages in sequence:
    1. Preprocessing: Clean AIS data, compute haversine distances
    2. Feature Engineering: Aggregate vessel features, compute baseline CO₂
    3. Training: Train RandomForestRegressor, display feature importance
    4. Evaluation: Evaluate model performance with RMSE and R²
    """
    print("\n" + "█" * 70)
    print("█" + " " * 68 + "█")
    print("█" + "  MARITIME CARBON EMISSION ML PIPELINE - FULL EXECUTION  ".center(68) + "█")
    print("█" + " " * 68 + "█")
    print("█" * 70 + "\n")
    
    try:
        # Stage 1: Preprocessing
        print("\n🔹 STAGE 1/4: DATA PREPROCESSING\n")
        preprocess()
        
        # Stage 2: Feature Engineering
        print("\n\n🔹 STAGE 2/4: FEATURE ENGINEERING\n")
        engineer_features()
        
        # Stage 3: Model Training
        print("\n\n🔹 STAGE 3/4: MODEL TRAINING\n")
        train_model()
        
        # Stage 4: Model Evaluation
        print("\n\n🔹 STAGE 4/4: MODEL EVALUATION\n")
        evaluate_model()
        
        # Success message
        print("\n" + "█" * 70)
        print("█" + " " * 68 + "█")
        print("█" + "  ✓ PIPELINE EXECUTION COMPLETE  ".center(68) + "█")
        print("█" + " " * 68 + "█")
        print("█" * 70)
        
        print("\n📁 Generated Outputs:")
        print("  • data/processed/ais_cleaned.csv")
        print("  • data/features/ais_features.csv")
        print("  • models/emission_model.pkl")
        
        print("\n🎯 Next Steps:")
        print("  • Review model performance metrics above")
        print("  • Integrate model into FastAPI backend")
        print("  • Use for real-time ESG scoring")
        
    except Exception as e:
        print("\n" + "❌ " * 35)
        print(f"ERROR: Pipeline execution failed!")
        print(f"Details: {str(e)}")
        print("❌ " * 35)
        raise


if __name__ == "__main__":
    main()
