"""
Configuration module for FastAPI backend.
Contains AWS S3 settings and application configuration.
"""

import os
from typing import Optional


class Settings:
    """Application settings and configuration."""
    
    # Application settings
    APP_NAME: str = "Maritime ESG Analytics API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # AWS S3 Configuration
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", "ai-carbon-esg-data-prajwal")
    S3_PREFIX: str = os.getenv("S3_PREFIX", "processed/features/")
    
    # AWS credentials (loaded from IAM role or environment variables)
    # Do NOT hardcode AWS keys here
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    
    # CORS settings
    CORS_ORIGINS: list = [
        "http://localhost:3000",  # React default dev server
        "http://localhost:3001",
        "*"  # Allow all origins for now (tighten in production)
    ]


# Create a global settings instance
settings = Settings()
