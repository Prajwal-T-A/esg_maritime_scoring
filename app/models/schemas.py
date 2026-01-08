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
