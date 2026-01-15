#!/usr/bin/env python3
"""
Weather-Enriched ML Inference Implementation Test
Verifies that all new components are correctly integrated.
"""

import asyncio
import sys
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_weather_service():
    """Test weather service initialization and API."""
    logger.info("Testing Weather Service...")
    try:
        from app.services.weather_service import get_weather_service, fetch_weather
        
        service = get_weather_service()
        assert service is not None, "Weather service should not be None"
        
        # Test fetch with default weather (no API key scenario)
        weather = await fetch_weather(1.3521, 103.8198)  # Singapore
        assert weather is not None, "Weather data should not be None"
        assert 'wind_speed_ms' in weather, "Weather should have wind_speed_ms"
        assert 'weather_resistance_factor' in weather, "Weather should have resistance factor"
        assert 'storm_flag' in weather, "Weather should have storm_flag"
        assert 'rough_sea_flag' in weather, "Weather should have rough_sea_flag"
        
        logger.info(f"✓ Weather Service OK")
        logger.info(f"  - Wind: {weather['wind_speed_ms']} m/s")
        logger.info(f"  - Resistance Factor: {weather['weather_resistance_factor']}")
        logger.info(f"  - Storm Flag: {weather['storm_flag']}")
        return True
    except Exception as e:
        logger.error(f"✗ Weather Service FAILED: {e}", exc_info=True)
        return False


async def test_live_emission_service():
    """Test live emission service."""
    logger.info("Testing Live Emission Service...")
    try:
        from app.services.live_emission_service import (
            get_live_emission_service,
            compute_adjusted_emissions
        )
        
        service = get_live_emission_service()
        assert service is not None, "Live emission service should not be None"
        
        # Test computation
        result = compute_adjusted_emissions(
            avg_speed=12.5,
            speed_std=2.0,
            distance_km=150.0,
            time_at_sea_hours=48.0,
            acceleration_events=5,
            length=200.0,
            width=30.0,
            draft=10.0,
            co2_factor=3.5,
            weather_resistance_factor=1.1
        )
        
        assert 'base_co2_kg' in result, "Result should have base_co2_kg"
        assert 'adjusted_co2_kg' in result, "Result should have adjusted_co2_kg"
        assert 'delta_due_to_weather' in result, "Result should have delta_due_to_weather"
        assert result['adjusted_co2_kg'] > result['base_co2_kg'], "Adjusted should be higher with resistance factor > 1"
        
        logger.info(f"✓ Live Emission Service OK")
        logger.info(f"  - Base CO2: {result['base_co2_kg']:.2f} kg")
        logger.info(f"  - Adjusted CO2: {result['adjusted_co2_kg']:.2f} kg")
        logger.info(f"  - Delta: {result['delta_due_to_weather']:.2f} kg")
        return True
    except Exception as e:
        logger.error(f"✗ Live Emission Service FAILED: {e}", exc_info=True)
        return False


async def test_weather_enriched_analysis():
    """Test weather-enriched analysis integration."""
    logger.info("Testing Weather-Enriched Analysis...")
    try:
        from app.services.live_tracking_service import live_tracking_service
        
        # Test the weather-enriched analysis method
        result = await live_tracking_service._calculate_weather_enriched_analysis(
            mmsi="123456789",
            speed=12.5,
            lat=1.3521,
            lon=103.8198
        )
        
        assert result is not None, "Analysis result should not be None"
        assert 'score' in result, "Result should have ESG score"
        assert 'rating' in result, "Result should have rating"
        assert 'weather' in result, "Result should have weather data"
        assert 'emissions' in result, "Result should have emissions data"
        assert result['score'] >= 0 and result['score'] <= 100, "ESG score should be 0-100"
        
        logger.info(f"✓ Weather-Enriched Analysis OK")
        logger.info(f"  - ESG Score: {result['score']}")
        logger.info(f"  - Rating: {result['rating']}")
        logger.info(f"  - Base CO2: {result.get('base_co2', 'N/A')} kg")
        logger.info(f"  - Weather Factor: {result['weather']['weather_resistance_factor']}")
        logger.info(f"  - Risk Flags: {result['risk_flags']}")
        return True
    except Exception as e:
        logger.error(f"✗ Weather-Enriched Analysis FAILED: {e}", exc_info=True)
        return False


async def test_schemas():
    """Test Pydantic schemas."""
    logger.info("Testing Pydantic Schemas...")
    try:
        from app.models.schemas import (
            WeatherData,
            WeatherAdjustedEmissions,
            LiveTrackingPayload
        )
        
        # Test WeatherData schema
        weather = WeatherData(
            wind_speed_ms=8.5,
            wind_direction_deg=180,
            condition="rain",
            wave_height_m=2.5,
            timestamp="2026-01-15T10:30:00Z",
            weather_resistance_factor=1.12,
            storm_flag=False,
            rough_sea_flag=False
        )
        assert weather.wind_speed_ms == 8.5
        
        # Test WeatherAdjustedEmissions schema
        emissions = WeatherAdjustedEmissions(
            base_co2_kg=5000.0,
            adjusted_co2_kg=5600.0,
            delta_due_to_weather=600.0,
            adjusted_speed_knots=13.2,
            weather_resistance_factor=1.1
        )
        assert emissions.base_co2_kg == 5000.0
        
        logger.info(f"✓ Pydantic Schemas OK")
        return True
    except Exception as e:
        logger.error(f"✗ Pydantic Schemas FAILED: {e}", exc_info=True)
        return False


async def test_config():
    """Test config loading."""
    logger.info("Testing Configuration...")
    try:
        from app.config import settings
        
        assert settings.APP_NAME == "Maritime ESG Analytics API"
        assert settings.APP_VERSION == "1.0.0"
        assert settings.OPENWEATHER_API_KEY is not None
        
        logger.info(f"✓ Configuration OK")
        logger.info(f"  - App Name: {settings.APP_NAME}")
        logger.info(f"  - Version: {settings.APP_VERSION}")
        logger.info(f"  - OpenWeather API Key: {'Set' if settings.OPENWEATHER_API_KEY else 'Not set (using defaults)'}")
        return True
    except Exception as e:
        logger.error(f"✗ Configuration FAILED: {e}", exc_info=True)
        return False


async def main():
    """Run all tests."""
    logger.info("=" * 70)
    logger.info("Weather-Enriched ML Inference Implementation Test Suite")
    logger.info("=" * 70)
    
    results = {}
    
    # Run tests
    results['config'] = await test_config()
    results['schemas'] = await test_schemas()
    results['weather_service'] = await test_weather_service()
    results['live_emission_service'] = await test_live_emission_service()
    results['weather_enriched_analysis'] = await test_weather_enriched_analysis()
    
    # Summary
    logger.info("=" * 70)
    logger.info("Test Summary")
    logger.info("=" * 70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("\n✓ All tests PASSED!")
        return 0
    else:
        logger.error(f"\n✗ {total - passed} test(s) FAILED!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
