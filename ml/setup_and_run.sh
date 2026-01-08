#!/bin/bash

# ML Pipeline Setup and Execution Script
# Maritime Carbon Emission Estimation
# 
# This script sets up the environment and runs the complete ML pipeline

set -e  # Exit on error

echo "════════════════════════════════════════════════════════════════"
echo "  Maritime Carbon Emission ML Pipeline - Setup & Execution"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Check Python version
echo "✓ Checking Python version..."
python3 --version || python --version

# Install dependencies
echo ""
echo "✓ Installing dependencies..."
pip install -q pandas numpy scikit-learn

# Verify data files exist
echo ""
echo "✓ Verifying input data files..."
if [ ! -f "data/raw/ais_raw.csv" ]; then
    echo "❌ ERROR: data/raw/ais_raw.csv not found!"
    echo "   Please ensure AIS data is in place before running pipeline."
    exit 1
fi

if [ ! -f "data/raw/emission_factors.csv" ]; then
    echo "❌ ERROR: data/raw/emission_factors.csv not found!"
    echo "   Please ensure emission factors data is in place before running pipeline."
    exit 1
fi

echo "   ✓ ais_raw.csv found"
echo "   ✓ emission_factors.csv found"

# Run pipeline
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  Starting ML Pipeline Execution"
echo "════════════════════════════════════════════════════════════════"
echo ""

python3 run_pipeline.py || python run_pipeline.py

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  ✅ Pipeline Complete!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Generated outputs:"
echo "  📁 data/processed/ais_cleaned.csv"
echo "  📁 data/features/ais_features.csv"
echo "  📁 models/emission_model.pkl"
echo ""
echo "Next steps:"
echo "  1. Review model metrics printed above"
echo "  2. Integrate model into FastAPI backend"
echo "  3. Use for real-time ESG scoring"
echo ""
