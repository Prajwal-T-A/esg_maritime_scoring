# ML Pipeline Quick Reference

## 🚀 Quick Commands

```bash
# Full pipeline execution
python run_pipeline.py

# Individual stages
python preprocessing/preprocess_ais.py
python features/feature_engineering.py
python training/train_emission_model.py
python evaluation/evaluate_model.py
```

## 📊 Data Flow

```
ais_raw.csv 
    ↓ [preprocess_ais.py]
ais_cleaned.csv 
    ↓ [feature_engineering.py]
ais_features.csv 
    ↓ [train_emission_model.py]
emission_model.pkl
    ↓ [evaluate_model.py]
Performance Metrics
```

## 🔑 Key Features Computed

1. **avg_speed** - Mean vessel speed
2. **speed_std** - Speed variability
3. **total_distance_km** - Haversine-computed distance
4. **time_at_sea_hours** - Total operational time
5. **acceleration_events** - Speed change count
6. **length, width, draft** - Vessel dimensions
7. **co2_factor** - Emission factor from lookup
8. **baseline_co2** - Target variable (kg CO₂)

## 📈 Model Configuration

- **Algorithm:** RandomForestRegressor
- **Trees:** 100
- **Max Depth:** 10
- **Train/Test:** 80/20 split
- **Random Seed:** 42

## 🎯 Evaluation Metrics

- **RMSE:** Root Mean Squared Error (kg CO₂)
- **R²:** Coefficient of Determination (0-1 scale)
- **MAE:** Mean Absolute Error (kg CO₂)

## 🔧 Configuration

All settings in `config.py`:
- File paths
- Model parameters
- Constants (Earth radius, thresholds)

## ⚡ Quick Checks

```bash
# Verify input data
ls data/raw/ais_raw.csv
ls data/raw/emission_factors.csv

# Check outputs
ls data/processed/ais_cleaned.csv
ls data/features/ais_features.csv
ls models/emission_model.pkl

# Inspect generated data
head -n 5 data/processed/ais_cleaned.csv
head -n 5 data/features/ais_features.csv
```

## 🐍 Python Usage

```python
import pickle
import pandas as pd

# Load trained model
with open('models/emission_model.pkl', 'rb') as f:
    model = pickle.load(f)

# Load features
features = pd.read_csv('data/features/ais_features.csv')

# Make prediction
prediction = model.predict(features[numeric_columns])
```

## 📝 Column Reference

### AIS Raw Data
- mmsi, base_date_time, longitude, latitude
- sog, cog, heading
- vessel_type, length, width, draft, cargo
- status, imo

### AIS Cleaned (adds)
- distance_km (haversine)
- time_diff_seconds

### AIS Features (vessel-level)
- avg_speed, speed_std
- total_distance_km, time_at_sea_hours
- acceleration_events
- co2_factor, fuel_type
- baseline_co2 (target)

## 🎓 Formula Reference

**Haversine Distance:**
```
a = sin²(Δlat/2) + cos(lat₁) × cos(lat₂) × sin²(Δlon/2)
c = 2 × arcsin(√a)
distance = R × c  (R = 6371 km)
```

**Baseline CO₂:**
```
fuel_burn_proxy = avg_speed × total_distance_km
baseline_co2 = fuel_burn_proxy × co2_factor × 0.1
```

## ⚠️ Common Issues

**Import Error:** Run from `ml/` directory
**Missing Data:** Check `data/raw/` has both CSVs
**Low Performance:** Review data quality, increase trees
**Memory Issues:** Reduce dataset size or max_depth

## 📞 Integration Points

**FastAPI Endpoint Example:**
```python
@app.post("/predict-emissions")
async def predict(vessel_data: VesselFeatures):
    features = extract_features(vessel_data)
    co2 = emission_model.predict([features])[0]
    return {"co2_kg": co2, "esg_score": compute_score(co2)}
```

---
**Ready for production integration** ✅
