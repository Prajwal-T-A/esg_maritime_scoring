# Maritime Carbon Emission ML Pipeline

Research-grade machine learning pipeline for estimating vessel CO₂ emissions and supporting ESG environmental scoring using real AIS (Automatic Identification System) data.

## 📋 Overview

This pipeline processes maritime AIS data to:
- Clean and validate vessel positioning and speed data
- Compute distance traveled using haversine formula
- Engineer vessel-level behavioral features
- Train interpretable Random Forest regression model
- Predict baseline CO₂ emissions for ESG scoring

**Language:** Python 3.10+  
**ML Library:** scikit-learn  
**Execution:** Local macOS system  
**Design:** Interpretable, research-grade, FastAPI-ready

---

## 📁 Project Structure

```
ml/
├── config.py                          # Centralized configuration
├── run_pipeline.py                    # Full pipeline executor
├── preprocessing/
│   ├── __init__.py
│   └── preprocess_ais.py             # AIS data cleaning & haversine distance
├── features/
│   ├── __init__.py
│   └── feature_engineering.py        # Vessel aggregation & baseline CO₂
├── training/
│   ├── __init__.py
│   └── train_emission_model.py       # RandomForest training
├── evaluation/
│   ├── __init__.py
│   └── evaluate_model.py             # RMSE & R² evaluation
├── models/
│   └── emission_model.pkl            # Trained model (generated)
└── data/
    ├── raw/
    │   ├── ais_raw.csv               # NOAA AIS data (input)
    │   └── emission_factors.csv      # IMO/IPCC factors (input)
    ├── processed/
    │   └── ais_cleaned.csv           # Cleaned AIS (generated)
    └── features/
        └── ais_features.csv          # Vessel features (generated)
```

---

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.10+ required
python --version

# Install dependencies
pip install pandas numpy scikit-learn
```

### Run Full Pipeline

```bash
# Execute all stages (preprocessing → features → training → evaluation)
cd ml
python run_pipeline.py
```

### Run Individual Stages

```bash
# Stage 1: Preprocess AIS data
python preprocessing/preprocess_ais.py

# Stage 2: Engineer features
python features/feature_engineering.py

# Stage 3: Train model
python training/train_emission_model.py

# Stage 4: Evaluate model
python evaluation/evaluate_model.py
```

---

## 📊 Pipeline Stages

### 1️⃣ Preprocessing (`preprocess_ais.py`)

**Input:** `data/raw/ais_raw.csv`  
**Output:** `data/processed/ais_cleaned.csv`

**Operations:**
- Parse `base_date_time` as datetime
- Remove invalid coordinates (lat/lon outside valid ranges)
- Remove invalid speeds (null or negative `sog`)
- Sort by `mmsi` and `base_date_time`
- **Compute haversine distance** between consecutive AIS points
- Compute time differences (seconds) between transmissions

**Key Formula:** Haversine distance for great-circle distance on Earth

### 2️⃣ Feature Engineering (`feature_engineering.py`)

**Input:** `data/processed/ais_cleaned.csv`, `data/raw/emission_factors.csv`  
**Output:** `data/features/ais_features.csv`

**Vessel-Level Features:**
- `avg_speed`: Mean speed over ground (knots)
- `speed_std`: Speed variability
- `total_distance_km`: Sum of haversine distances
- `time_at_sea_hours`: Total time span in dataset
- `acceleration_events`: Count of speed changes > threshold
- Vessel metadata: `length`, `width`, `draft`, `vessel_type`, `cargo`

**Emission Calculation:**
```python
fuel_burn_proxy = avg_speed × total_distance_km
baseline_co2 = fuel_burn_proxy × co2_factor × scaling_constant
```

### 3️⃣ Model Training (`train_emission_model.py`)

**Input:** `data/features/ais_features.csv`  
**Output:** `models/emission_model.pkl`

**Model:** `RandomForestRegressor`
- **n_estimators:** 100
- **max_depth:** 10
- **Test size:** 20%
- **Random seed:** 42

**Features Used:** All numeric features (speed, distance, dimensions, etc.)  
**Target:** `baseline_co2` (kg CO₂)

**Outputs:**
- Feature importance rankings
- Quick train/test performance check
- Saved model (.pkl)

### 4️⃣ Model Evaluation (`evaluate_model.py`)

**Input:** `models/emission_model.pkl`, `data/features/ais_features.csv`  
**Output:** Console metrics display

**Metrics:**
- **RMSE** (Root Mean Squared Error): Average prediction error in kg CO₂
- **R² Score**: Proportion of variance explained (0 to 1)
- **MAE** (Mean Absolute Error): Typical absolute error

**Interpretations:**
- R² ≥ 0.9: Excellent
- R² ≥ 0.7: Good
- R² ≥ 0.5: Moderate
- R² < 0.5: Poor

---

## 📈 Configuration (`config.py`)

Centralized settings for:
- File paths (all stages reference this)
- Model hyperparameters (n_estimators, max_depth, etc.)
- Constants (Earth radius, acceleration threshold, random seed)

**No hardcoded paths elsewhere.**

---

## 🔬 Design Principles

### Interpretability First
- **Random Forest** chosen for feature importance
- Clear docstrings and comments throughout
- Metric explanations in evaluation output

### Research-Grade Quality
- Haversine formula for accurate distance calculation
- Physics-based baseline CO₂ estimation
- Proper train/test split with fixed seed for reproducibility

### Production-Ready
- Modular design for FastAPI integration
- Centralized configuration
- Clean code with error handling
- Pickle model for easy loading

### No Deep Learning
- Scikit-learn only
- Interpretable tree-based models
- No cloud dependencies (runs locally)

---

## 📝 Data Requirements

### AIS Data (`ais_raw.csv`)

Required columns:
- `mmsi`: Maritime Mobile Service Identity (vessel ID)
- `base_date_time`: Timestamp
- `longitude`, `latitude`: Position
- `sog`: Speed over ground (knots)
- `vessel_type`: Vessel classification
- `length`, `width`, `draft`: Vessel dimensions
- `cargo`: Cargo type

### Emission Factors (`emission_factors.csv`)

Required columns:
- `vessel_type`: Must match AIS vessel types
- `fuel_type`: Fuel classification
- `co2_factor`: CO₂ emission factor

---

## 🎯 Use Cases

### ESG Environmental Scoring
- Estimate vessel CO₂ emissions from AIS tracks
- Compare fleet environmental performance
- Support maritime sustainability reporting

### Research Applications
- Maritime emission modeling
- Vessel behavior analysis
- ML benchmarking for AIS data

### Integration
- FastAPI backend for real-time inference
- Batch processing for fleet analysis
- Feature engineering for extended ESG metrics

---

## ⚙️ Model Details

**Algorithm:** Random Forest Regression

**Why Random Forest?**
- Handles non-linear relationships
- Robust to outliers and missing data
- No feature scaling needed
- Built-in feature importance
- Interpretable through decision paths

**Feature Importance:**
Model automatically ranks which features most influence CO₂ predictions:
- Typically: `total_distance_km`, `avg_speed`, vessel dimensions
- Used for model interpretation and feature selection

---

## 📌 Important Notes

### Data Handling
- ✅ Uses real AIS data (no mock data generation)
- ✅ Uses AIS-provided vessel types (no heuristic inference)
- ✅ Preserves vessel metadata from AIS records

### Limitations
- Baseline CO₂ is **simplified physics model** (not real-time sensor data)
- Linear fuel burn assumption (actual is ~cubic with speed)
- Does not account for weather, sea state, or hull fouling

### Future Enhancements
- Add weather data integration
- Implement speed-power cubic relationship
- Cross-validation for robustness testing
- Hyperparameter tuning (Grid/RandomSearch)

---

## 🔗 Integration with FastAPI

Load trained model in backend:

```python
import pickle
from pathlib import Path

MODEL_PATH = Path("ml/models/emission_model.pkl")

with open(MODEL_PATH, 'rb') as f:
    emission_model = pickle.load(f)

# Use for prediction
features = [...]  # Extract from AIS data
co2_prediction = emission_model.predict([features])[0]
```

---

## 📚 References

- **Haversine Formula:** Great-circle distance calculation
- **Random Forest:** Breiman, L. (2001). "Random Forests"
- **IPCC Guidelines:** CO₂ emission factors
- **IMO Data:** International Maritime Organization standards

---

## 👨‍💻 Development

**Clean Code Practices:**
- Comprehensive docstrings (Google style)
- Type hints where applicable
- Modular functions for testability
- Logging for debugging

**Testing:**
```bash
# Verify data files exist
ls data/raw/

# Check outputs after pipeline
ls data/processed/
ls data/features/
ls models/
```

---

## 📄 License

Research and educational use. Consult with legal team before commercial deployment.

---

## 🆘 Troubleshooting

**Issue:** `FileNotFoundError` for CSV files  
**Solution:** Ensure `ais_raw.csv` and `emission_factors.csv` exist in `data/raw/`

**Issue:** Low R² score  
**Solution:** Check data quality, consider more features, tune hyperparameters

**Issue:** Import errors  
**Solution:** Run from `ml/` directory or adjust `sys.path`

---

**Built for research-grade ESG environmental scoring** 🌊🌍
