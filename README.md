# Maritime ESG Analytics Platform

Research-grade ML pipeline for maritime carbon emission estimation and ESG environmental scoring, powered by FastAPI backend and React frontend.

## Project Overview

A full-stack platform for analyzing vessel environmental performance using real AIS (Automatic Identification System) data. The system combines a RandomForest ML model for CO₂ emission predictions with deterministic ESG environmental scoring to provide comprehensive vessel analytics.

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.9+)
- **ML Model**: scikit-learn RandomForest
- **Cloud**: AWS S3 for data storage
- **API**: RESTful endpoints with ML prediction integration

### Frontend
- **Framework**: React.js 18.2.0
- **Routing**: react-router-dom 6.20.0
- **Styling**: Tailwind CSS 3.3.6 with glass-morphism design
- **HTTP Client**: Axios 1.6.2

### ML Pipeline
- **Model**: RandomForest Regressor
- **Features**: 9 vessel/operational metrics
- **Target**: CO₂ emissions (kg)
- **Scoring**: Deterministic ESG environmental scoring (0-100)

## Project Structure

```
ESG_Scoring_Pipeline/
├── app/                     # Backend (FastAPI)
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration and settings
│   ├── api/
│   │   └── routes.py        # API endpoints (health, analyze-vessel)
│   ├── services/
│   │   └── s3_service.py    # S3 data access layer
│   └── models/
│       └── schemas.py       # Pydantic data models
├── frontend/                # Frontend (React)
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.jsx          # Main app with routing
│   │   ├── index.js         # Entry point
│   │   ├── pages/
│   │   │   ├── Landing.jsx  # Welcome page
│   │   │   ├── AnalyzeVessel.jsx  # Main analysis interface
│   │   │   └── Home.jsx     # Legacy page
│   │   ├── components/
│   │   │   ├── ESGScoreCard.jsx
│   │   │   ├── HealthStatus.jsx
│   │   │   ├── VesselHistory.jsx
│   │   │   └── VesselLatest.jsx
│   │   └── services/
│   │       └── api.js       # API communication layer
│   ├── package.json
│   └── tailwind.config.js   # Custom Tailwind configuration
├── ml/                      # ML Pipeline
│   ├── data/
│   │   └── raw/
│   │       ├── ais_raw.csv
│   │       └── emission_factors.csv
│   └── esg/                 # ESG scoring logic
├── Test_Files/              # Test JSON samples (gitignored)
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Features

### ML-Powered Predictions
- RandomForest model predicting CO₂ emissions based on vessel operational data
- 9 input features: MMSI, speed metrics, distance, time at sea, acceleration events, vessel dimensions, CO₂ factor
- Research-grade accuracy with real AIS training data

### ESG Environmental Scoring
- Deterministic scoring algorithm (0-100 scale)
- Color-coded ratings: Excellent (90+), Good (70+), Fair (50+), Poor (30+), Critical (<30)
- Environmental risk flags for high emissions, excessive speed, long voyages
- Actionable recommendations for improvement

### Modern UI/UX
- Landing page with maritime background and professional glass-morphism design
- Vessel analysis interface with comprehensive form inputs
- Real-time results display with ESG gauge, KPI cards, and risk alerts
- Responsive design with Tailwind CSS
- No sign-up required for instant analysis

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

### 2. Analyze Vessel (ML Prediction)
```
POST /api/v1/analyze-vessel
```
Predict CO₂ emissions and calculate ESG score for a vessel.

**Request Body:**
```json
{
  "mmsi": "123456789",
  "avg_speed": 12.5,
  "speed_std": 2.3,
  "total_distance_km": 450.0,
  "time_at_sea_hours": 36.0,
  "acceleration_events": 15,
  "length": 180.0,
  "width": 28.0,
  "draft": 10.5,
  "co2_factor": 3.2
}
```

**Response:**
```json
{
  "mmsi": "123456789",
  "estimated_co2_kg": 1245.67,
  "esg_score": 75,
  "rating": "Good",
  "description": "Above average environmental performance",
  "recommendation": "Continue current practices and monitor emissions trends",
  "risk_flags": ["High average speed detected"]
}
```

### 3. Legacy Endpoints (S3 Data)

#### Latest Vessel Data
```
GET /api/v1/vessels/{mmsi}/latest
```
Fetch the most recent AIS record for a specific vessel.

**Parameters:**
- `mmsi` (path): Maritime Mobile Service Identity

**Response:** AISRecord object

#### Vessel History
```
GET /api/v1/vessels/{mmsi}/history
```
Fetch all historical AIS records for a vessel, sorted by timestamp.

**Parameters:**
- `mmsi` (path): Maritime Mobile Service Identity

**Response:** Array of AISRecord objects

#### ESG Metrics
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

## Quick Start

### Backend Setup

1. **Navigate to project directory:**
   ```bash
   cd /Users/prajwal_t_a/Desktop/Coding/ESG_Scoring_Pipeline
   ```

2. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # macOS/Linux
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the backend:**
   ```bash
   uvicorn app.main:app --reload
   ```
   
   Backend will run at `http://localhost:8000`
   - API docs: `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```
   
   Frontend will run at `http://localhost:3000`

### Access the Application

- **Landing Page**: `http://localhost:3000/`
- **Analyze Vessel**: `http://localhost:3000/analyze`
- **API Documentation**: `http://localhost:8000/docs`

## Configuration

### AWS S3 (Optional - for legacy endpoints)
Configure AWS credentials for S3-based endpoints:
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-east-1
export S3_BUCKET_NAME=ai-carbon-esg-data-prajwal
```

### Environment Variables
- `DEBUG`: Enable debug mode (default: `False`)
- `S3_BUCKET_NAME`: S3 bucket name
- `S3_PREFIX`: S3 key prefix (default: `processed/features/`)
- `AWS_REGION`: AWS region (default: `us-east-1`)

## Design System

### Frontend Styling
- **Design Pattern**: Glass-morphism with backdrop blur effects
- **Color Palette**: Cyan/blue gradients, transparent overlays, red alerts, green success
- **Background**: Maritime operations imagery with dark gradient overlay
- **Cards**: Semi-transparent with subtle white borders (bg-white/10, border-white/30)
- **Forms**: Transparent inputs with cyan focus rings
- **Animations**: Fade-in effects (0.8s), pulse animations (3s)

### ESG Score Color Coding
- **90-100**: Green (Excellent)
- **70-89**: Lime (Good)
- **50-69**: Yellow (Fair)
- **30-49**: Orange (Poor)
- **0-29**: Red (Critical)

## Data Flow

1. **User Input**: Vessel operational data entered in React form (AnalyzeVessel page)
2. **API Request**: Frontend sends POST request to `/api/v1/analyze-vessel`
3. **ML Prediction**: Backend loads RandomForest model and predicts CO₂ emissions
4. **ESG Scoring**: Deterministic algorithm calculates environmental score
5. **Risk Analysis**: System identifies environmental risk flags
6. **Response**: Results displayed with ESG gauge, KPI cards, recommendations, and alerts

## CORS Configuration

CORS is configured to allow requests from:
- `http://localhost:3000` (React dev server)
- `http://localhost:3001`

**Production**: Update `CORS_ORIGINS` in [app/config.py](app/config.py) to restrict origins.

## Testing

Test the ML prediction endpoint:
```bash
curl -X POST http://localhost:8000/api/v1/analyze-vessel \
  -H "Content-Type: application/json" \
  -d '{
    "mmsi": "123456789",
    "avg_speed": 12.5,
    "speed_std": 2.3,
    "total_distance_km": 450.0,
    "time_at_sea_hours": 36.0,
    "acceleration_events": 15,
    "length": 180.0,
    "width": 28.0,
    "draft": 10.5,
    "co2_factor": 3.2
  }'
```

## Project Features Summary

✅ **ML Pipeline**: RandomForest model for CO₂ emission predictions  
✅ **ESG Scoring**: Deterministic environmental scoring with risk flags  
✅ **Modern UI**: Glass-morphism design with maritime backgrounds  
✅ **Real-time Analysis**: Instant vessel analysis with comprehensive results  
✅ **RESTful API**: FastAPI backend with ML integration  
✅ **Responsive Design**: Mobile-friendly Tailwind CSS styling  
✅ **No Authentication**: Instant access without sign-up

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

### Adding New Features

**Backend (FastAPI)**:
1. Add route in [app/api/routes.py](app/api/routes.py)
2. Create Pydantic schema in [app/models/schemas.py](app/models/schemas.py)
3. Add business logic in [app/services/](app/services/)

**Frontend (React)**:
1. Create component in [frontend/src/components/](frontend/src/components/)
2. Add page in [frontend/src/pages/](frontend/src/pages/)
3. Update routing in [frontend/src/App.jsx](frontend/src/App.jsx)
4. Add API call in [frontend/src/services/api.js](frontend/src/services/api.js)

### Code Standards
- **Python**: PEP 8, type hints, docstrings
- **JavaScript**: ES6+, functional components, hooks
- **Styling**: Tailwind utility classes, glass-morphism patterns

## Deployment

### Frontend (Static Hosting)
- Build: `npm run build` in frontend directory
- Deploy to: Vercel, Netlify, AWS S3 + CloudFront
- Environment: Set API base URL for production

### Backend (FastAPI)
- **AWS Lambda**: Package with dependencies, use API Gateway
- **Docker**: Build container and deploy to ECS/EKS
- **EC2**: Run with systemd/supervisor, nginx reverse proxy

Example Dockerfile:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app ./app
COPY ml ./ml
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Troubleshooting

### Backend Issues

**ML Model Not Found**  
Ensure the trained model exists in the `ml/` directory with correct path in code.

**CORS Errors**  
Check that frontend URL is in `CORS_ORIGINS` in [app/config.py](app/config.py).

**Import Errors**  
Verify all dependencies are installed: `pip install -r requirements.txt`

### Frontend Issues

**API Connection Failed**  
Verify backend is running at `http://localhost:8000` and check browser console for errors.

**Blank Page**  
Check browser console for errors, ensure all dependencies installed: `npm install`

**Styling Issues**  
Clear browser cache, verify Tailwind config in [frontend/tailwind.config.js](frontend/tailwind.config.js)

## Future Enhancements

- [ ] Real-time vessel tracking with live AIS data feeds
- [ ] Historical trend analysis and comparison charts
- [ ] Fleet-wide analytics and benchmarking
- [ ] PDF report generation with ESG metrics
- [ ] Authentication and user accounts
- [ ] Rate limiting and API keys
- [ ] Comprehensive test suite (unit, integration, E2E)
- [ ] CI/CD pipeline with GitHub Actions
- [ ] Database integration for storing analysis history
- [ ] Advanced ML models (Neural Networks, ensemble methods)

## Tech Stack Details

**Backend Dependencies**:
- fastapi
- uvicorn
- boto3 (AWS S3)
- scikit-learn
- pandas
- numpy
- pydantic

**Frontend Dependencies**:
- react
- react-router-dom
- axios
- tailwindcss
- autoprefixer
- postcss

## License

Proprietary - Internal use only

## Contact

For questions or issues, contact the development team.
