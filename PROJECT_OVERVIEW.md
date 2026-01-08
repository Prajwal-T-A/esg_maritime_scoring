# 🚢 Maritime ESG Analytics - Complete Project Guide

## Project Overview

Full-stack sustainability analytics application for tracking maritime vessel carbon emissions and ESG environmental scores.

### Tech Stack
- **Backend**: FastAPI (Python)
- **Frontend**: React.js + Tailwind CSS
- **Cloud**: AWS (S3, Lambda)
- **Data**: Processed AIS records with ESG metrics

---

## 📁 Complete Project Structure

```
ESG_Scoring_Pipeline/
│
├── app/                          # Backend (FastAPI)
│   ├── __init__.py
│   ├── main.py                   # FastAPI application
│   ├── config.py                 # Configuration
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py             # API endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   └── s3_service.py         # S3 data access
│   └── models/
│       ├── __init__.py
│       └── schemas.py            # Pydantic models
│
├── frontend/                     # Frontend (React)
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/           # Reusable components
│   │   │   ├── HealthStatus.js
│   │   │   ├── VesselLatest.js
│   │   │   ├── VesselHistory.js
│   │   │   └── ESGScoreCard.js
│   │   ├── pages/
│   │   │   └── Home.js           # Main page
│   │   ├── services/
│   │   │   └── api.js            # API service layer
│   │   ├── App.js                # Main app
│   │   ├── index.js              # Entry point
│   │   └── index.css             # Global styles
│   ├── package.json
│   ├── tailwind.config.js
│   └── .env                      # Backend URL config
│
├── Test_Files/                   # Sample AIS data
│   ├── ais_sample_001.json
│   ├── ais_sample_002.json
│   └── ...
│
├── requirements.txt              # Python dependencies
├── README.md                     # Backend documentation
└── QUICKSTART.md                 # Quick start guide
```

---

## 🚀 Complete Setup Guide

### Part 1: Backend Setup

```bash
# 1. Navigate to project root
cd /Users/prajwal_t_a/Desktop/Coding/ESG_Scoring_Pipeline

# 2. Create virtual environment
python3 -m venv venv

# 3. Activate virtual environment
source venv/bin/activate

# 4. Install backend dependencies
pip install -r requirements.txt

# 5. Configure AWS credentials
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key  
# Enter region: us-east-1

# 6. Start backend server
uvicorn app.main:app --reload
```

**Backend will run on**: `http://127.0.0.1:8000`

**Verify backend**: Open `http://127.0.0.1:8000/docs` in browser

---

### Part 2: Frontend Setup

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install frontend dependencies
npm install

# 3. Start React development server
npm start
```

**Frontend will run on**: `http://localhost:3000`

**Browser opens automatically** with the application

---

## 🎯 How the System Works

### Data Flow

```
AWS S3 Bucket
    ↓
  (Processed AIS data with ESG scores)
    ↓
FastAPI Backend (Port 8000)
    ↓
  (REST APIs: /latest, /history, /esg)
    ↓
React Frontend (Port 3000)
    ↓
  (User Interface)
```

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/health` | GET | Backend health check |
| `/api/v1/vessels/{mmsi}/latest` | GET | Latest vessel record |
| `/api/v1/vessels/{mmsi}/history` | GET | Historical records |
| `/api/v1/esg/{mmsi}` | GET | ESG metrics only |

### Data Schema

```json
{
  "mmsi": "419001234",
  "speed_knots": 14.5,
  "latitude": 12.9716,
  "longitude": 77.5946,
  "timestamp": "2026-01-06T18:30:00Z",
  "estimated_co2_kg": 0.29,
  "esg_environment_score": 70
}
```

---

## 🎨 Frontend Features

### 1. Health Status Indicator
- **Location**: Top header
- **Purpose**: Shows backend connectivity
- **Colors**: 
  - 🟢 Green = Connected
  - 🔴 Red = Disconnected
  - 🟡 Yellow = Checking

### 2. MMSI Input & Fetch
- **Input field**: Enter vessel MMSI
- **3 Buttons**:
  - Latest Data
  - History
  - ESG Metrics

### 3. Latest Data View
- **Left Panel**: Vessel information
  - Location (lat/lon)
  - Speed in knots
  - Timestamp
  - CO₂ emissions
  - ESG score
- **Right Panel**: ESG Score Card
  - Large score display
  - Color-coded performance
  - Score interpretation

### 4. History View
- **Table format** with columns:
  - Timestamp
  - Location
  - Speed
  - CO₂
  - ESG Score
- **Footer**: Average calculations
- **Color-coded** ESG scores

### 5. ESG Score Card
- **Score Display**: Large, centered
- **Color Coding**:
  - 🟢 Green (80-100): Excellent
  - 🟠 Orange (60-79): Moderate
  - 🔴 Red (<60): Needs Improvement
- **Additional Info**:
  - CO₂ emissions
  - Timestamp
  - Score guide

---

## 🧪 Testing the Application

### Test Scenario 1: Latest Data

```
1. Start backend (port 8000)
2. Start frontend (port 3000)
3. Enter MMSI: 419001234
4. Click "Latest Data"
5. Verify:
   ✓ Vessel location displayed
   ✓ Speed shown in knots
   ✓ CO₂ emissions displayed
   ✓ ESG score card shows with color
```

### Test Scenario 2: History

```
1. Enter MMSI: 419001234
2. Click "History"
3. Verify:
   ✓ Table appears with multiple records
   ✓ Timestamps are sorted
   ✓ Average calculations shown
   ✓ ESG scores are color-coded
```

### Test Scenario 3: Error Handling

```
1. Enter invalid MMSI: 999999999
2. Click any button
3. Verify:
   ✓ Error message displayed
   ✓ Red error banner appears
   ✓ Helpful error detail shown
```

---

## 🎓 Viva Preparation Guide

### Key Points to Explain

#### 1. **Architecture**
- 3-tier architecture: Frontend → Backend → Data Storage
- RESTful API design
- Separation of concerns

#### 2. **Backend (FastAPI)**
- **Why FastAPI?**
  - Fast performance
  - Automatic API documentation
  - Type checking with Pydantic
  
- **Key Components**:
  - `main.py`: Application setup, CORS, routing
  - `routes.py`: API endpoint definitions
  - `s3_service.py`: S3 data access logic
  - `schemas.py`: Data validation models

#### 3. **Frontend (React)**
- **Why React?**
  - Component-based architecture
  - Virtual DOM for performance
  - Rich ecosystem
  
- **Key Concepts**:
  - **Components**: Reusable UI pieces
  - **State**: Data that changes (useState)
  - **Props**: Data passed to components
  - **Hooks**: useEffect for side effects

- **Component Structure**:
  ```
  Home (Page)
    ├── HealthStatus
    ├── VesselLatest
    ├── VesselHistory
    └── ESGScoreCard
  ```

#### 4. **Data Flow**
```
User enters MMSI
  ↓
React state updated
  ↓
API call triggered (axios)
  ↓
FastAPI receives request
  ↓
S3Service fetches from S3
  ↓
Data returned to FastAPI
  ↓
JSON response sent
  ↓
React receives data
  ↓
State updated
  ↓
Component re-renders
  ↓
UI updates
```

#### 5. **Styling**
- **Tailwind CSS utility-first approach**
- **Responsive design**: Works on mobile and desktop
- **Color scheme**: Semantic colors for ESG scores

#### 6. **Error Handling**
- Try-catch in API calls
- User-friendly error messages
- Loading states for UX

---

## 📊 Code Walkthrough for Viva

### Backend: API Endpoint Example

```python
@router.get("/vessels/{mmsi}/latest")
async def get_latest_vessel_data(mmsi: str):
    """Fetch latest vessel data"""
    # Call S3 service
    latest_record = s3_service.get_latest_vessel_record(mmsi)
    
    # Handle not found
    if not latest_record:
        raise HTTPException(status_code=404, detail="Not found")
    
    # Return data
    return latest_record
```

**Explain**:
- Route decorator defines endpoint
- Type hints for validation
- S3 service handles data fetching
- HTTP exceptions for errors

### Frontend: Component Example

```jsx
function ESGScoreCard({ score, co2Emissions }) {
  // Determine color based on score
  const getColor = () => {
    if (score >= 80) return 'green';
    if (score >= 60) return 'orange';
    return 'red';
  };

  return (
    <div className={`bg-${getColor()}-100`}>
      <h3>ESG Score: {score}</h3>
      <p>CO₂: {co2Emissions} kg</p>
    </div>
  );
}
```

**Explain**:
- Props receive data from parent
- Function determines color logic
- Tailwind classes for styling
- Dynamic class names based on data

---

## 🐛 Troubleshooting Guide

### Backend Issues

**Problem**: "ModuleNotFoundError: No module named 'app'"
```bash
# Solution: Run from project root
cd /Users/prajwal_t_a/Desktop/Coding/ESG_Scoring_Pipeline
uvicorn app.main:app --reload
```

**Problem**: "AWS credentials not found"
```bash
# Solution: Configure AWS CLI
aws configure
```

**Problem**: "No data found for MMSI"
- Check if MMSI exists in S3
- Verify S3 bucket permissions
- Check S3 prefix in config.py

### Frontend Issues

**Problem**: "Backend is not responding"
```bash
# Solution: Start backend
cd /Users/prajwal_t_a/Desktop/Coding/ESG_Scoring_Pipeline
source venv/bin/activate
uvicorn app.main:app --reload
```

**Problem**: "Cannot find module 'react'"
```bash
# Solution: Install dependencies
cd frontend
npm install
```

**Problem**: "Port 3000 already in use"
```bash
# Solution: Use different port
PORT=3001 npm start
```

---

## 📈 Performance & Scalability

### Current Setup
- **Backend**: Handles concurrent requests
- **Frontend**: Client-side rendering
- **Data**: Read-only S3 access

### Future Improvements
1. **Caching**: Redis for frequently accessed data
2. **Pagination**: For large history datasets
3. **Real-time**: WebSocket for live updates
4. **Authentication**: JWT tokens
5. **Database**: PostgreSQL for faster queries
6. **CDN**: CloudFront for frontend

---

## 🔒 Security Considerations

### Current Implementation
✅ No hardcoded AWS credentials
✅ CORS configured for security
✅ Input validation with Pydantic
✅ Read-only S3 access
✅ Error messages don't expose internals

### Production Recommendations
- Add authentication (JWT)
- Implement rate limiting
- Use HTTPS only
- Restrict CORS to specific origins
- Add request logging
- Implement API key validation

---

## 📝 Key Files Explained

### Backend

**`app/main.py`**
- FastAPI application setup
- CORS middleware
- Route registration
- Global error handling

**`app/api/routes.py`**
- All API endpoints
- Request validation
- Response formatting
- Error handling

**`app/services/s3_service.py`**
- S3 client initialization
- Data fetching logic
- Timestamp sorting
- JSON parsing

**`app/config.py`**
- Environment variables
- S3 bucket configuration
- Application settings

### Frontend

**`src/App.js`**
- React Router setup
- Main application structure

**`src/pages/Home.js`**
- Main page logic
- State management
- API calls
- UI composition

**`src/services/api.js`**
- Centralized API calls
- Axios configuration
- Error handling
- Response formatting

**`src/components/`**
- Reusable UI components
- Props-based data display
- Conditional rendering

---

## ✅ Pre-Viva Checklist

### Preparation
- [ ] Backend running successfully
- [ ] Frontend running successfully
- [ ] Health indicator shows green
- [ ] Can fetch latest data
- [ ] Can view history
- [ ] Can view ESG metrics
- [ ] Errors handled gracefully

### Know How to Explain
- [ ] Overall architecture
- [ ] Data flow from S3 to UI
- [ ] Backend API endpoints
- [ ] React component structure
- [ ] State management
- [ ] ESG scoring logic
- [ ] Color coding system
- [ ] Error handling

### Demonstrate
- [ ] Enter MMSI and fetch data
- [ ] Show all three views (latest, history, ESG)
- [ ] Point out health indicator
- [ ] Show error handling (invalid MMSI)
- [ ] Explain code in any file

---

## 🎯 Summary

**What You Built**:
A full-stack web application that displays maritime vessel sustainability metrics by reading processed AIS data from AWS S3, serving it through a FastAPI backend, and visualizing it in a React frontend with intuitive ESG score cards and historical analysis.

**Technologies Used**:
- Backend: Python, FastAPI, boto3, Pydantic
- Frontend: React.js, Tailwind CSS, Axios
- Cloud: AWS S3
- Tools: npm, pip, uvicorn

**Key Features**:
- Real-time backend health monitoring
- Latest vessel data display
- Historical data table
- Color-coded ESG scores
- Responsive design
- Error handling

**Ready for deployment and demonstration! 🚀**
