"""
API Routes for Maritime ESG Analytics.
Defines all REST API endpoints for vessel data and ESG metrics.
"""

from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException, status

from app.models.schemas import (
    AISRecord,
    ESGResponse,
    HealthResponse,
    ErrorResponse
)
from app.services.s3_service import s3_service

# Create API router
router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check if the API is running and responsive"
)
async def health_check():
    """
    Health check endpoint.
    Returns the current status of the API.
    """
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


@router.get(
    "/vessels/{mmsi}/latest",
    response_model=AISRecord,
    summary="Get Latest Vessel Data",
    description="Fetch the most recent AIS record for a specific vessel",
    responses={
        200: {"description": "Successfully retrieved latest vessel record"},
        404: {"model": ErrorResponse, "description": "Vessel not found or no data available"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def get_latest_vessel_data(mmsi: str):
    """
    Fetch the latest processed AIS record for a given MMSI.
    
    Args:
        mmsi: Maritime Mobile Service Identity (vessel identifier)
        
    Returns:
        Latest AIS record with all fields including ESG metrics
        
    Raises:
        HTTPException: 404 if no data found for the MMSI
    """
    try:
        # Fetch latest record from S3
        latest_record = s3_service.get_latest_vessel_record(mmsi)
        
        if not latest_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No data found for MMSI: {mmsi}"
            )
        
        return latest_record
    
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching vessel data: {str(e)}"
        )


@router.get(
    "/vessels/{mmsi}/history",
    response_model=List[AISRecord],
    summary="Get Vessel History",
    description="Fetch all historical AIS records for a specific vessel, sorted by timestamp",
    responses={
        200: {"description": "Successfully retrieved vessel history"},
        404: {"model": ErrorResponse, "description": "Vessel not found or no data available"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def get_vessel_history(mmsi: str):
    """
    Fetch all processed AIS records for a given MMSI, sorted by timestamp.
    
    Args:
        mmsi: Maritime Mobile Service Identity (vessel identifier)
        
    Returns:
        List of AIS records sorted from oldest to newest
        
    Raises:
        HTTPException: 404 if no data found for the MMSI
    """
    try:
        # Fetch all records from S3
        history = s3_service.get_vessel_history(mmsi)
        
        if not history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No historical data found for MMSI: {mmsi}"
            )
        
        return history
    
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching vessel history: {str(e)}"
        )


@router.get(
    "/esg/{mmsi}",
    response_model=ESGResponse,
    summary="Get ESG Metrics",
    description="Fetch ESG-specific metrics for a vessel (CO2 emissions and environment score)",
    responses={
        200: {"description": "Successfully retrieved ESG metrics"},
        404: {"model": ErrorResponse, "description": "Vessel not found or no ESG data available"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def get_vessel_esg_metrics(mmsi: str):
    """
    Fetch ESG metrics for a given vessel.
    Returns MMSI, estimated CO2 emissions, ESG environment score, and timestamp.
    
    Args:
        mmsi: Maritime Mobile Service Identity (vessel identifier)
        
    Returns:
        ESG metrics including CO2 emissions and environment score
        
    Raises:
        HTTPException: 404 if no ESG data found for the MMSI
    """
    try:
        # Fetch ESG data from S3
        esg_data = s3_service.get_vessel_esg_data(mmsi)
        
        if not esg_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No ESG data found for MMSI: {mmsi}"
            )
        
        return esg_data
    
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching ESG data: {str(e)}"
        )
