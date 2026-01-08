"""
Example script demonstrating how to interact with the Maritime ESG Analytics API.
This can be used for testing the API endpoints locally.
"""

import requests
import json
from typing import Optional


class ESGAPIClient:
    """Simple client for testing the ESG Analytics API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL of the API (default: http://localhost:8000)
        """
        self.base_url = base_url
        self.api_prefix = "/api/v1"
    
    def health_check(self) -> dict:
        """Check API health status."""
        url = f"{self.base_url}{self.api_prefix}/health"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_latest_vessel_data(self, mmsi: str) -> dict:
        """Get the latest data for a vessel."""
        url = f"{self.base_url}{self.api_prefix}/vessels/{mmsi}/latest"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_vessel_history(self, mmsi: str) -> list:
        """Get historical data for a vessel."""
        url = f"{self.base_url}{self.api_prefix}/vessels/{mmsi}/history"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_esg_metrics(self, mmsi: str) -> dict:
        """Get ESG metrics for a vessel."""
        url = f"{self.base_url}{self.api_prefix}/esg/{mmsi}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()


def main():
    """Main function to test API endpoints."""
    # Initialize client
    client = ESGAPIClient()
    
    print("=" * 60)
    print("Maritime ESG Analytics API - Test Script")
    print("=" * 60)
    
    # Test 1: Health Check
    print("\n1. Testing Health Check Endpoint...")
    try:
        health = client.health_check()
        print(f"✓ Health Check: {json.dumps(health, indent=2)}")
    except Exception as e:
        print(f"✗ Health Check Failed: {e}")
        return
    
    # Test 2: Get Latest Vessel Data
    print("\n2. Testing Latest Vessel Data Endpoint...")
    test_mmsi = input("Enter MMSI to test (or press Enter to skip): ").strip()
    
    if test_mmsi:
        try:
            latest = client.get_latest_vessel_data(test_mmsi)
            print(f"✓ Latest Data for MMSI {test_mmsi}:")
            print(json.dumps(latest, indent=2))
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"✗ No data found for MMSI: {test_mmsi}")
            else:
                print(f"✗ Error: {e}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 3: Get Vessel History
        print("\n3. Testing Vessel History Endpoint...")
        try:
            history = client.get_vessel_history(test_mmsi)
            print(f"✓ Found {len(history)} historical records for MMSI {test_mmsi}")
            if history:
                print("First record:")
                print(json.dumps(history[0], indent=2))
                if len(history) > 1:
                    print(f"\nLast record:")
                    print(json.dumps(history[-1], indent=2))
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"✗ No historical data found for MMSI: {test_mmsi}")
            else:
                print(f"✗ Error: {e}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 4: Get ESG Metrics
        print("\n4. Testing ESG Metrics Endpoint...")
        try:
            esg = client.get_esg_metrics(test_mmsi)
            print(f"✓ ESG Metrics for MMSI {test_mmsi}:")
            print(json.dumps(esg, indent=2))
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"✗ No ESG data found for MMSI: {test_mmsi}")
            else:
                print(f"✗ Error: {e}")
        except Exception as e:
            print(f"✗ Error: {e}")
    else:
        print("Skipping vessel data tests (no MMSI provided)")
    
    print("\n" + "=" * 60)
    print("Testing Complete!")
    print("=" * 60)
    print("\nAPI Documentation available at:")
    print(f"  - Swagger UI: {client.base_url}/docs")
    print(f"  - ReDoc: {client.base_url}/redoc")
    print("=" * 60)


if __name__ == "__main__":
    print("\nMake sure the API server is running:")
    print("  uvicorn app.main:app --reload\n")
    
    input("Press Enter to start testing...")
    main()
