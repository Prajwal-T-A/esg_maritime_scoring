# ESG Environmental Scoring Module

Deterministic and explainable environmental scoring system for maritime vessels.

---

## 📊 Overview

This module computes environmental ESG scores (0-100) for vessels based on:
- **CO₂ emission intensity** (kg per km traveled)
- **Operational efficiency** (acceleration patterns, speed optimization)
- **Duration optimization** (route planning efficiency)

### Score Range
- **90-100:** Excellent environmental performance ⭐
- **70-89:** Good environmental performance ✓
- **50-69:** Moderate environmental performance ○
- **30-49:** Poor environmental performance ⚠
- **0-29:** Critical environmental performance ❌

---

## 🎯 Key Features

### ✅ Deterministic
- Same inputs always produce identical outputs
- Reproducible across systems and time
- No randomness or external dependencies

### ✅ Explainable
- Clear penalty system with policy reasoning
- Risk flags identify specific issues
- Human-readable interpretations

### ✅ Actionable
- Risk flags guide improvement efforts
- Fleet-level summaries identify patterns
- Benchmark against top performers

---

## 📐 Scoring Algorithm

### Starting Score
All vessels start with a perfect score of **100**

### Penalties Applied

| Risk Factor | Threshold | Penalty | Policy Reasoning |
|-------------|-----------|---------|------------------|
| **High CO₂ Intensity** | > 50 kg/km | -25 points | Primary environmental impact metric |
| **Excessive Acceleration** | > 20 events | -15 points | Operational inefficiency indicator |
| **High Speed** | > 18 knots | -10 points | Speed ∝ fuel consumption³ |
| **Extended Duration** | > 720 hours | -10 points | Possible route inefficiency |

### CO₂ Intensity Calculation
```python
co2_intensity = baseline_co2 / total_distance_km
```

Special cases:
- If `total_distance_km = 0` and `baseline_co2 > 0`: intensity = ∞ (maximum penalty)
- If both are 0: intensity = 0 (no penalty)

---

## 🚀 Usage

### Basic Scoring

```python
from ml.esg.esg_scoring import compute_esg_score, get_score_interpretation

# Compute score for a vessel
score, risk_flags = compute_esg_score(
    baseline_co2=5000.0,          # kg CO₂
    total_distance_km=100.0,       # km
    avg_speed=12.0,                # knots
    acceleration_events=5,         # count
    time_at_sea_hours=48.0        # hours
)

print(f"ESG Score: {score}/100")
print(f"Risk Flags: {risk_flags}")

# Get interpretation
interpretation = get_score_interpretation(score)
print(f"Rating: {interpretation['rating']}")
print(f"Recommendation: {interpretation['recommendation']}")
```

### Fleet-Level Analysis

```python
from ml.esg.esg_scoring import compute_fleet_esg_summary

# Prepare fleet data
fleet_data = [
    ('VESSEL_001', 95, []),
    ('VESSEL_002', 85, []),
    ('VESSEL_003', 65, ['High CO2 intensity']),
]

# Get fleet summary
summary = compute_fleet_esg_summary(fleet_data)
print(f"Fleet Average: {summary['fleet_average_score']}/100")
print(f"Excellent: {summary['excellent_count']} vessels")
print(f"Common Risks: {summary['most_common_risks']}")
```

### Score Entire Fleet from Features

```python
# Run the integrated fleet scoring
python ml/esg/score_fleet.py
```

This will:
1. Load vessel features from `ml/data/features/ais_features.csv`
2. Compute ESG scores for all vessels
3. Display top/bottom performers
4. Save results to `ml/data/features/vessel_esg_scores.csv`

---

## 📊 Example Output

### Individual Vessel
```
ESG Score: 100/100
Rating: Excellent
Risk Flags: None
Recommendation: Industry-leading practices. Share best practices with fleet.
```

### Poor Performer
```
ESG Score: 40/100
Rating: Poor
Risk Flags:
  - High CO2 intensity (100.00 kg/km > 50.0 kg/km threshold)
  - Excessive acceleration events (35 > 20 threshold)
  - High average speed (22.00 knots > 18.0 knots threshold)
  - Extended operational duration (800.00 hours > 720.0 hours threshold)
Recommendation: Immediate action required. Address all risk flags systematically.
```

### Fleet Summary
```
Fleet Average Score: 76.0/100
Performance Distribution:
  ⭐ Excellent (90-100): 2 vessels (40.0%)
  ✓  Good (70-89):      1 vessels (20.0%)
  ○  Moderate (50-69):  1 vessels (20.0%)
  ⚠  Poor (30-49):      1 vessels (20.0%)
  ❌ Critical (0-29):   0 vessels (0.0%)

Most Common Risks:
  1. High CO2 intensity
  2. Excessive acceleration
```

---

## 🔧 Customizing Thresholds

Thresholds can be adjusted for specific regulatory requirements or fleet benchmarks:

```python
from ml.esg.esg_scoring import update_thresholds, get_current_thresholds

# View current thresholds
thresholds = get_current_thresholds()
print(thresholds)

# Update thresholds (use cautiously - affects score comparability)
update_thresholds(
    co2_intensity=45.0,      # Stricter CO₂ limit
    avg_speed=16.0,          # Promote more slow steaming
    acceleration_events=15   # Stricter efficiency requirement
)
```

**⚠️ Warning:** Changing thresholds affects score comparability over time. Document all threshold changes for reproducibility.

---

## 📁 Module Files

- **`esg_scoring.py`** - Core scoring logic and utilities
- **`score_fleet.py`** - Fleet-level integration with ML pipeline
- **`__init__.py`** - Module initialization

---

## 🎓 Policy Reasoning

### Why These Thresholds?

**CO₂ Intensity (50 kg/km)**
- Based on industry benchmarks for efficient vessels
- Aligns with IMO emissions targets
- Balances strictness with achievability

**Acceleration Events (20)**
- Derived from operational best practices
- Smooth operations reduce wear and emissions
- Typical for well-planned voyages

**Speed Limit (18 knots)**
- Optimal cruising speed for many vessel types
- Balances efficiency with schedule requirements
- Based on slow steaming research (fuel ∝ speed³)

**Duration (720 hours / 30 days)**
- Reasonable threshold for transoceanic routes
- Flags potentially inefficient scheduling
- Context-dependent interpretation needed

---

## 🔗 Integration with ML Pipeline

The ESG scoring module integrates seamlessly with the emission prediction pipeline:

```
AIS Data → Feature Engineering → Emission Model → ESG Scoring → Dashboard
```

**Workflow:**
1. ML model predicts `baseline_co2` emissions
2. ESG module computes environmental score
3. Risk flags identify improvement opportunities
4. FastAPI serves scores to frontend dashboard

---

## 📈 Real-World Results

From the current dataset (16,367 vessels):
- **Fleet Average:** 98.35/100 ⭐
- **Excellent Performance:** 89.4% of fleet
- **Vessels with Risks:** 11.1%
- **Most Common Risk:** Excessive acceleration events

This indicates a generally efficient fleet with targeted improvement opportunities in operational smoothness.

---

## 🧪 Testing

Run the module tests:

```bash
# Test with example scenarios
python ml/esg/esg_scoring.py

# Test fleet integration
python ml/esg/score_fleet.py
```

---

## 📚 References

- **IMO MARPOL Annex VI** - Ship emission regulations
- **IPCC Guidelines** - CO₂ emission factors
- **Slow Steaming Research** - Speed-fuel consumption relationship
- **ESG Frameworks** - Environmental scoring best practices

---

## 🎯 Future Enhancements

Potential extensions:
- [ ] Weather impact adjustment
- [ ] Vessel class-specific thresholds
- [ ] Temporal trend analysis
- [ ] Peer group benchmarking
- [ ] Carbon offset calculations
- [ ] Regulatory compliance checking

---

**Built for transparent, actionable environmental assessment** 🌍⚓
