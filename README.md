# Maritime ESG Analytics - FastAPI Backend

Production-ready FastAPI backend for serving maritime freight carbon emissions and ESG analytics data from Amazon S3 to a React frontend.

## Project Overview

This backend API serves processed AIS (Automatic Identification System) data with carbon emissions estimates and ESG environmental scores. The data is stored in Amazon S3 and served via RESTful APIs.

## Architecture

- **Framework**: FastAPI (Python)
- **Cloud Provider**: AWS
- **Storage**: Amazon S3 (`ai-carbon-esg-data-prajwal`)
- **Data Location**: `s3://ai-carbon-esg-data-prajwal/processed/features/`
- **Deployment**: AWS Lambda-ready (can also run locally or on EC2)

## Project Structure

```
ESG_Scoring_Pipeline/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration and settings
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py        # API endpoint definitions
│   ├── services/
│   │   ├── __init__.py
│   │   └── s3_service.py    # S3 data access layer
│   └── models/
│       ├── __init__.py
│       └── schemas.py       # Pydantic data models
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Data Schema

Each AIS record in S3 has the following structure:

```json
{
  "mmsi": "string",
  "speed_knots": float,
  "latitude": float,
  "longitude": float,
  "timestamp": "ISO 8601 string",
  "estimated_co2_kg": float,
  "esg_environment_score": int
}
```

## API Endpoints

### 1. Health Check
```
GET /api/v1/health
```
Returns API health status.

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2026-01-08T10:30:00Z"
}
```

### 2. Latest Vessel Data
```
GET /api/v1/vessels/{mmsi}/latest
```
Fetch the most recent AIS record for a specific vessel.

**Parameters:**
- `mmsi` (path): Maritime Mobile Service Identity

**Response:** AISRecord object

### 3. Vessel History
```
GET /api/v1/vessels/{mmsi}/history
```
Fetch all historical AIS records for a vessel, sorted by timestamp.

**Parameters:**
- `mmsi` (path): Maritime Mobile Service Identity

**Response:** Array of AISRecord objects

### 4. ESG Metrics
```
GET /api/v1/esg/{mmsi}
```
Fetch ESG-specific metrics for a vessel.

**Parameters:**
- `mmsi` (path): Maritime Mobile Service Identity

**Response:**
```json
{
  "mmsi": "123456789",
  "estimated_co2_kg": 145.3,
  "esg_environment_score": 75,
  "timestamp": "2026-01-08T10:30:00Z"
}
```

## Setup Instructions

### Prerequisites

- Python 3.9 or higher
- AWS credentials configured (IAM role or environment variables)
- Access to S3 bucket: `ai-carbon-esg-data-prajwal`

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd /Users/prajwal_t_a/Desktop/Coding/ESG_Scoring_Pipeline
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure AWS credentials:**
   
   Option A - Environment variables:
   ```bash
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   export AWS_REGION=us-east-1
   ```
   
   Option B - AWS CLI configuration:
   ```bash
   aws configure
   ```
   
   Option C - IAM role (when deployed on AWS)

### Running Locally

1. **Start the development server:**
   ```bash
   uvicorn app.main:app --reload
   ```
   
   Or run directly:
   ```bash
   python -m app.main
   ```

2. **Access the API:**
   - API base URL: `http://localhost:8000`
   - Swagger UI (interactive docs): `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

3. **Test the health endpoint:**
   ```bash
   curl http://localhost:8000/api/v1/health
   ```

### Environment Variables

Optional environment variables for configuration:

- `S3_BUCKET_NAME`: S3 bucket name (default: `ai-carbon-esg-data-prajwal`)
- `S3_PREFIX`: S3 key prefix (default: `processed/features/`)
- `AWS_REGION`: AWS region (default: `us-east-1`)
- `DEBUG`: Enable debug mode (default: `False`)

Example:
```bash
export S3_BUCKET_NAME=ai-carbon-esg-data-prajwal
export AWS_REGION=us-east-1
export DEBUG=True
```

## CORS Configuration

CORS is configured to allow requests from:
- `http://localhost:3000` (React dev server)
- `http://localhost:3001`
- All origins (`*`) for development

**Production:** Update `CORS_ORIGINS` in [app/config.py](app/config.py) to restrict origins.

## Error Handling

The API includes comprehensive error handling:

- **404 Not Found**: Vessel MMSI not found or no data available
- **500 Internal Server Error**: S3 access errors, invalid JSON, etc.
- All errors return JSON with `error` and `detail` fields

Example error response:
```json
{
  "error": "Resource not found",
  "detail": "No data found for MMSI: 123456789"
}
```

## Security Notes

- **No AWS credentials in code**: Uses IAM roles or environment variables
- **Read-only S3 access**: Backend never writes to S3
- **CORS protection**: Configure allowed origins before production deployment
- **Input validation**: All inputs validated using Pydantic models

## Development

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Document all functions with docstrings

### Adding New Endpoints

1. Add route function in [app/api/routes.py](app/api/routes.py)
2. Create Pydantic model in [app/models/schemas.py](app/models/schemas.py) if needed
3. Add business logic in [app/services/s3_service.py](app/services/s3_service.py) if needed

## Deployment Options

### AWS Lambda
- Package the application with dependencies
- Configure Lambda to use IAM role for S3 access
- Use AWS API Gateway as trigger

### Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app ./app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### EC2 / ECS
- Install dependencies on instance
- Use systemd or supervisor to manage the process
- Configure nginx as reverse proxy

## Future Enhancements

- [ ] Add caching layer (Redis) for frequently accessed data
- [ ] Implement pagination for history endpoint
- [ ] Add filtering and query parameters
- [ ] Integrate ML model predictions
- [ ] Add authentication (JWT tokens)
- [ ] Implement rate limiting
- [ ] Add comprehensive test suite
- [ ] Set up CI/CD pipeline

## Troubleshooting

### Issue: AWS credentials not found
**Solution:** Configure AWS credentials using `aws configure` or set environment variables.

### Issue: S3 bucket access denied
**Solution:** Ensure your IAM user/role has `s3:GetObject` and `s3:ListBucket` permissions for the bucket.

### Issue: No data returned for MMSI
**Solution:** Verify that processed files exist in `s3://ai-carbon-esg-data-prajwal/processed/features/` and contain the queried MMSI.

## License

Proprietary - Internal use only

## Contact

For questions or issues, contact the development team.
