"""
Test script for the /predict-emissions endpoint.

This script tests the ML inference API endpoint locally.
"""

import requests
import json

# API endpoint
BASE_URL = "http://localhost:8000"
PREDICT_ENDPOINT = f"{BASE_URL}/predict-emissions"

# Test payload - sample vessel features
test_payload = {
    "mmsi": "367123456",
    "avg_speed": 12.5,
    "speed_std": 2.1,
    "total_distance_km": 150.0,
    "time_at_sea_hours": 48.0,
    "acceleration_events": 5,
    "length": 200.0,
    "width": 30.0,
    "draft": 10.0,
    "co2_factor": 3.206
}

print("="*70)
print("TESTING ML PREDICTION ENDPOINT")
print("="*70)
print(f"\nEndpoint: {PREDICT_ENDPOINT}")
print(f"\nRequest payload:")
print(json.dumps(test_payload, indent=2))

try:
    # Make POST request
    response = requests.post(PREDICT_ENDPOINT, json=test_payload)
    
    print(f"\nResponse status: {response.status_code}")
    print(f"\nResponse body:")
    print(json.dumps(response.json(), indent=2))
    
    if response.status_code == 200:
        print("\n✅ SUCCESS: Prediction endpoint is working!")
        result = response.json()
        print(f"\nMMSI: {result['mmsi']}")
        print(f"Estimated CO₂: {result['estimated_co2_kg']:.2f} kg")
    else:
        print(f"\n❌ ERROR: Request failed with status {response.status_code}")
        
except requests.exceptions.ConnectionError:
    print("\n❌ ERROR: Could not connect to API server")
    print("Make sure FastAPI is running: uvicorn app.main:app --reload")
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")

print("\n" + "="*70)
