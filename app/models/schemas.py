"""
Pydantic models for request/response schemas.
Defines data structures for AIS records and API responses.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class AISRecord(BaseModel):
    """Schema for a single AIS record with ESG data."""
    
    mmsi: str = Field(..., description="Maritime Mobile Service Identity")
    speed_knots: float = Field(..., description="Vessel speed in knots")
    latitude: float = Field(..., description="Vessel latitude coordinate")
    longitude: float = Field(..., description="Vessel longitude coordinate")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    estimated_co2_kg: float = Field(..., description="Estimated CO2 emissions in kg")
    esg_environment_score: int = Field(..., description="ESG environmental score")
    
    class Config:
        json_schema_extra = {
            "example": {
                "mmsi": "123456789",
                "speed_knots": 12.5,
                "latitude": 37.7749,
                "longitude": -122.4194,
                "timestamp": "2026-01-08T10:30:00Z",
                "estimated_co2_kg": 145.3,
                "esg_environment_score": 75
            }
        }


class ESGResponse(BaseModel):
    """Schema for ESG-specific endpoint response."""
    
    mmsi: str = Field(..., description="Maritime Mobile Service Identity")
    estimated_co2_kg: float = Field(..., description="Estimated CO2 emissions in kg")
    esg_environment_score: int = Field(..., description="ESG environmental score")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "mmsi": "123456789",
                "estimated_co2_kg": 145.3,
                "esg_environment_score": 75,
                "timestamp": "2026-01-08T10:30:00Z"
            }
        }


class HealthResponse(BaseModel):
    """Schema for health check endpoint."""
    
    status: str = Field(..., description="API health status")
    timestamp: Optional[str] = Field(None, description="Current server timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "ok",
                "timestamp": "2026-01-08T10:30:00Z"
            }
        }


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Resource not found",
                "detail": "No data found for MMSI: 123456789"
            }
        }


class EmissionPredictionRequest(BaseModel):
    """
    Schema for CO₂ emission prediction request.
    
    Contains vessel operational features used by the ML model to estimate
    baseline CO₂ emissions. All features must match the training data format.
    """
    
    mmsi: str = Field(..., description="Maritime Mobile Service Identity")
    avg_speed: float = Field(..., ge=0, le=50, description="Average speed over ground in knots")
    speed_std: float = Field(..., ge=0, le=20, description="Standard deviation of speed in knots")
    total_distance_km: float = Field(..., ge=0, description="Total distance traveled in kilometers")
    time_at_sea_hours: float = Field(..., ge=0, description="Total operational time in hours")
    acceleration_events: int = Field(..., ge=0, description="Count of significant speed change events")
    length: float = Field(..., ge=0, le=500, description="Vessel length in meters")
    width: float = Field(..., ge=0, le=100, description="Vessel width in meters")
    draft: float = Field(..., ge=0, le=50, description="Vessel draft in meters")
    co2_factor: float = Field(..., ge=0, le=10, description="CO₂ emission factor (kg CO₂ per fuel unit)")
    
    class Config:
        json_schema_extra = {
            "example": {
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
        }


class EmissionPredictionResponse(BaseModel):
    """
    Schema for CO₂ emission prediction response.
    
    Returns the vessel MMSI and the ML model's predicted CO₂ emissions.
    """
    
    mmsi: str = Field(..., description="Maritime Mobile Service Identity")
    estimated_co2_kg: float = Field(..., description="Predicted baseline CO₂ emissions in kilograms")
    
    class Config:
        json_schema_extra = {
            "example": {
                "mmsi": "367123456",
                "estimated_co2_kg": 5432.18
            }
        }


class VesselAnalysisResponse(BaseModel):
    """
    Schema for unified vessel analysis response.
    
    Combines ML emission prediction with ESG environmental scoring.
    """
    
    mmsi: str = Field(..., description="Maritime Mobile Service Identity")
    estimated_co2_kg: float = Field(..., description="ML-predicted baseline CO₂ emissions in kilograms")
    esg_score: int = Field(..., ge=0, le=100, description="ESG environmental score (0-100, higher is better)")
    rating: str = Field(..., description="ESG performance rating (Excellent/Good/Moderate/Poor/Critical)")
    description: str = Field(..., description="Human-readable score interpretation")
    recommendation: str = Field(..., description="Actionable improvement recommendations")
    risk_flags: list[str] = Field(..., description="List of environmental risk indicators")
    
    class Config:
        json_schema_extra = {
            "example": {
                "mmsi": "367123456",
                "estimated_co2_kg": 5432.18,
                "esg_score": 85,
                "rating": "Good",
                "description": "Good environmental performance",
                "recommendation": "Maintain current practices, minor optimizations possible.",
                "risk_flags": []
            }
        }
