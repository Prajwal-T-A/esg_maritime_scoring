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
    ErrorResponse,
    EmissionPredictionRequest,
    EmissionPredictionResponse,
    VesselAnalysisResponse,
    ChatRequest,
    ChatResponse,
    OllamaHealthResponse,
    WeatherData,
    WeatherAdjustedEmissions,
    LiveTrackingPayload
)
from app.services.s3_service import s3_service
from app.services.ml_service import predict_emissions
from app.services.analysis_service import analyze_vessel
from app.services.ollama_service import ollama_service

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


@router.post(
    "/predict-emissions",
    response_model=EmissionPredictionResponse,
    summary="Predict CO₂ Emissions",
    description="Predict baseline CO₂ emissions for a vessel using the trained ML model",
    responses={
        200: {"description": "Successfully predicted CO₂ emissions"},
        400: {"model": ErrorResponse, "description": "Invalid input data"},
        500: {"model": ErrorResponse, "description": "Internal server error or model failure"}
    },
    tags=["ML Predictions"]
)
async def predict_vessel_emissions(request: EmissionPredictionRequest):
    """
    Predict CO₂ emissions for a vessel using the trained RandomForest model.
    
    This endpoint takes vessel operational features and returns an estimated
    baseline CO₂ emission value in kilograms. The prediction is based on a
    trained machine learning model using historical AIS data.
    
    The model uses the following features (in order):
    1. avg_speed - Average speed over ground (knots)
    2. speed_std - Standard deviation of speed (knots)
    3. total_distance_km - Total distance traveled (km)
    4. time_at_sea_hours - Total operational time (hours)
    5. acceleration_events - Count of significant speed changes
    6. length - Vessel length (meters)
    7. width - Vessel width (meters)
    8. draft - Vessel draft (meters)
    9. co2_factor - CO₂ emission factor (kg CO₂ per fuel unit)
    
    Args:
        request: EmissionPredictionRequest containing all required features
        
    Returns:
        EmissionPredictionResponse with MMSI and predicted CO₂ emissions
        
    Raises:
        HTTPException: 400 if input validation fails
        HTTPException: 500 if model prediction fails
        
    Example:
        Request:
        ```json
        {
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
        ```
        
        Response:
        ```json
        {
            "mmsi": "367123456",
            "estimated_co2_kg": 5432.18
        }
        ```
    """
    try:
        # Convert request to dictionary for ML service
        # This keeps the ML service decoupled from Pydantic models
        features = {
            'avg_speed': request.avg_speed,
            'speed_std': request.speed_std,
            'total_distance_km': request.total_distance_km,
            'time_at_sea_hours': request.time_at_sea_hours,
            'acceleration_events': request.acceleration_events,
            'length': request.length,
            'width': request.width,
            'draft': request.draft,
            'co2_factor': request.co2_factor
        }
        
        # Call ML service to get prediction
        # This is a synchronous call - the model is fast enough for REST API
        estimated_co2 = predict_emissions(features)
        
        # Return response with MMSI and prediction
        return EmissionPredictionResponse(
            mmsi=request.mmsi,
            estimated_co2_kg=estimated_co2
        )
    
    except ValueError as e:
        # Input validation errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input data: {str(e)}"
        )
    except RuntimeError as e:
        # Model prediction errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )
    except Exception as e:
        # Unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.post(
    "/analyze-vessel",
    response_model=VesselAnalysisResponse,
    summary="Unified Vessel Analysis",
    description="Predict CO₂ emissions and compute ESG environmental score in one call",
    responses={
        200: {"description": "Successfully completed vessel analysis"},
        400: {"model": ErrorResponse, "description": "Invalid input data"},
        500: {"model": ErrorResponse, "description": "Analysis failed"}
    }
)
async def analyze_vessel_endpoint(request: EmissionPredictionRequest):
    """
    Unified analysis combining ML emission prediction and ESG scoring.
    
    This endpoint provides a complete environmental analysis by:
    1. Predicting CO₂ emissions using the ML model
    2. Computing ESG environmental score based on operational metrics
    3. Providing rating, interpretation, and actionable recommendations
    
    Args:
        request: EmissionPredictionRequest with all vessel operational features
        
    Returns:
        VesselAnalysisResponse containing:
        - mmsi: Vessel identifier
        - estimated_co2_kg: ML-predicted emissions
        - esg_score: Environmental score (0-100)
        - rating: Performance category
        - description: Score interpretation
        - recommendation: Improvement suggestions
        - risk_flags: Identified environmental concerns
        
    Raises:
        HTTPException: 400 if input validation fails
        HTTPException: 500 if analysis fails
    """
    try:
        # Call unified analysis service
        result = await analyze_vessel(
            mmsi=request.mmsi,
            avg_speed=request.avg_speed,
            speed_std=request.speed_std,
            total_distance_km=request.total_distance_km,
            time_at_sea_hours=request.time_at_sea_hours,
            acceleration_events=request.acceleration_events,
            length=request.length,
            width=request.width,
            draft=request.draft,
            co2_factor=request.co2_factor,
            generate_report=request.generate_report
        )
        
        return VesselAnalysisResponse(**result)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input data: {str(e)}"
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Chat with AI Assistant",
    description="Send a message to the ESG-focused AI chatbot and receive a response",
    responses={
        200: {"description": "Successfully received chat response"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def chat_with_assistant(request: ChatRequest):
    """
    Send a message to the Ollama-powered chatbot.
    
    Args:
        request: Chat request with message and optional conversation history
        
    Returns:
        AI assistant's response
    """
    try:
        # Convert Pydantic models to dict for service layer
        history = None
        if request.conversation_history:
            history = [msg.dict() for msg in request.conversation_history]
        
        response = await ollama_service.chat(
            message=request.message,
            conversation_history=history
        )
        
        return ChatResponse(**response)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat error: {str(e)}"
        )


@router.get(
    "/chat/health",
    response_model=OllamaHealthResponse,
    summary="Check Ollama Status",
    description="Check if Ollama is running and which models are available",
    responses={
        200: {"description": "Ollama health status"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def check_ollama_health():
    """
    Check Ollama service health and available models.
    
    Returns:
        Health status including available models
    """
    try:
        health_status = await ollama_service.check_health()
        return OllamaHealthResponse(**health_status)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check error: {str(e)}"
        )

# WebSocket endpoint for live tracking
from fastapi import WebSocket, WebSocketDisconnect
from app.services.live_tracking_service import live_tracking_service
from app.services.weather_service import get_weather_service
from app.services.live_emission_service import compute_adjusted_emissions
import asyncio


@router.get(
    "/weather/{lat}/{lon}",
    summary="Get Weather Data",
    description="Fetch real-time weather for a location (lat/lon)",
    responses={
        200: {"description": "Weather data retrieved successfully"},
        400: {"model": ErrorResponse, "description": "Invalid coordinates"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def get_weather(lat: float, lon: float):
    """
    Fetch real-time weather data for a specific latitude/longitude.
    
    Weather data includes wind, waves, conditions, and computed
    weather resistance factor for maritime operations.
    
    Args:
        lat: Latitude coordinate
        lon: Longitude coordinate
    
    Returns:
        Weather data with resistance factors and flags
    """
    try:
        if lat < -90 or lat > 90 or lon < -180 or lon > 180:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid coordinates: lat [-90,90], lon [-180,180]"
            )
        
        weather_service = get_weather_service()
        weather_data = await weather_service.fetch_weather(lat, lon)
        
        return {
            "latitude": lat,
            "longitude": lon,
            "timestamp": weather_data.get('timestamp'),
            "weather": weather_data
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Weather fetch error: {str(e)}"
        )


@router.post(
    "/emissions/weather-adjusted",
    summary="Compute Weather-Adjusted Emissions",
    description="Compute baseline and weather-adjusted CO2 emissions",
    responses={
        200: {"description": "Emissions computed successfully"},
        400: {"model": ErrorResponse, "description": "Invalid input"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def compute_weather_adjusted_emissions(request: EmissionPredictionRequest, weather_resistance_factor: float = 1.0):
    """
    Compute weather-adjusted CO2 emissions for a vessel.
    
    Takes baseline vessel parameters and a weather resistance factor,
    returns both baseline and weather-adjusted emissions.
    
    Args:
        request: Vessel operational parameters
        weather_resistance_factor: Weather multiplier (≥1.0)
    
    Returns:
        Base and weather-adjusted emissions with delta
    """
    try:
        if weather_resistance_factor < 1.0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Weather resistance factor must be ≥ 1.0"
            )
        
        result = compute_adjusted_emissions(
            avg_speed=request.avg_speed,
            speed_std=request.speed_std,
            distance_km=request.total_distance_km,
            time_at_sea_hours=request.time_at_sea_hours,
            acceleration_events=request.acceleration_events,
            length=request.length,
            width=request.width,
            draft=request.draft,
            co2_factor=request.co2_factor,
            weather_resistance_factor=weather_resistance_factor
        )
        
        return {
            "mmsi": request.mmsi,
            "emissions": result,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Emissions calculation error: {str(e)}"
        )


@router.websocket("/ws/live-vessels")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time vessel tracking.
    
    Streams vessel positions, weather data, and weather-adjusted ESG scores
    every 2 seconds. Payload includes:
    - Real-time position and heading
    - Weather conditions (wind, waves)
    - Baseline and weather-adjusted CO2 emissions
    - ESG score and rating
    - Risk flags (including weather-specific)
    
    Use this endpoint to subscribe to live vessel tracking with
    weather enrichment and ML-based ESG analysis.
    """
    await live_tracking_service.connect_client(websocket)
    try:
        # Start the background streamer if it's not running
        # In a production app, this should be a startup event or dedicated worker
        if not live_tracking_service.is_running:
             asyncio.create_task(live_tracking_service.stream_ais_data())
             
        while True:
            # Keep connection alive and listen for any client messages
            message = await websocket.receive_text()
            await live_tracking_service.handle_client_message(message)
            
    except WebSocketDisconnect:
        live_tracking_service.disconnect_client(websocket)
