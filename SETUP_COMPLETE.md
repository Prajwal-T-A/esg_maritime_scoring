# Maritime ESG Analytics - Complete Setup Guide

## ✅ Setup Complete!

Your project is now fully configured and ready to run.

### 📦 What Was Installed

#### Backend Dependencies
- ✅ FastAPI 0.115.0+ (REST API framework)
- ✅ Uvicorn 0.32.0+ (ASGI server)
- ✅ Pydantic 2.10.0+ (Data validation)
- ✅ Boto3 1.35.0+ (AWS S3 integration)
- ✅ Ollama 0.4.0+ (LLM integration)
- ✅ Pandas, NumPy, scikit-learn (ML pipeline)

#### Frontend Dependencies
- ✅ React 18.2.0 + React Router 6.20.0
- ✅ Tailwind CSS 3.3.6 (Styling)
- ✅ Axios 1.6.2 (HTTP client)
- ✅ Leaflet + react-leaflet (Map component)

#### Python Environment
- ✅ Virtual environment created at `.venv/`
- ✅ Python 3.13.1

---

## 🚀 Running the Project

### Option 1: Using VS Code Tasks (Recommended)

1. **Start Backend Server**
   - Press `Cmd+Shift+B` (macOS) or `Ctrl+Shift+B` (Windows/Linux)
   - Select "Start Backend Server"
   - Backend runs at `http://localhost:8000`
   - Swagger docs available at `http://localhost:8000/docs`

2. **Start Frontend Server** (in new terminal)
   - Press `Ctrl+Shift+` ` (backtick) to open new terminal
   - Press `Cmd+Shift+B` again
   - Select "Start Frontend Server"
   - Frontend runs at `http://localhost:3000`

3. **Open Application**
   - Visit `http://localhost:3000` in your browser

---

### Option 2: Manual Terminal Commands

#### Terminal 1 - Backend:
```bash
cd /Users/saiabhiram/Downloads/LocalDesktop/ESG_cloud/esg_maritime_scoring
.venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Terminal 2 - Frontend:
```bash
cd /Users/saiabhiram/Downloads/LocalDesktop/ESG_cloud/esg_maritime_scoring/frontend
npm start
```

---

## 🔧 Configuration

### Environment Variables
- Copy `.env.example` to `.env` if needed
- Default settings work for local development
- For AWS S3 access, ensure AWS credentials are configured (IAM role or `.aws/credentials`)

### Key Endpoints

**Backend API** (`http://localhost:8000`):
- `GET /api/v1/health` - Health check
- `POST /api/v1/analyze-vessel` - Analyze vessel ESG score
- `GET /docs` - Swagger UI documentation
- `GET /redoc` - ReDoc documentation

**Frontend** (`http://localhost:3000`):
- `/` - Landing page
- `/analyze` - Vessel analysis interface
- `/tracking` - Live tracking (if enabled)

---

## 🧪 Testing the API

### Using curl or Postman:

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Analyze vessel (example)
curl -X POST http://localhost:8000/api/v1/analyze-vessel \
  -H "Content-Type: application/json" \
  -d '{
    "mmsi": 123456789,
    "vessel_name": "Test Vessel",
    "speed_avg": 15.5,
    "speed_max": 22.0,
    "distance_traveled": 5000,
    "time_at_sea": 500,
    "co2_factor": 3.5,
    "length": 200,
    "width": 32
  }'
```

---

## 📊 ML Pipeline

To run the ML model training pipeline:

1. Ensure data files exist in `ml/data/raw/`:
   - `ais_raw.csv`
   - `emission_factors.csv`

2. Run via VS Code task:
   - Press `Cmd+Shift+B`
   - Select "Run ML Pipeline"

3. Or manually:
   ```bash
   .venv/bin/python ml/run_pipeline.py
   ```

---

## 🔍 Project Structure

```
esg_maritime_scoring/
├── app/                          # FastAPI backend
│   ├── main.py                   # Entry point
│   ├── config.py                 # Configuration
│   ├── api/routes.py             # API endpoints
│   ├── services/                 # Business logic
│   └── models/schemas.py         # Data models
├── frontend/                     # React frontend
│   ├── public/index.html
│   ├── src/
│   │   ├── App.jsx
│   │   ├── pages/                # Page components
│   │   ├── components/           # Reusable components
│   │   └── services/api.js       # API communication
│   └── package.json
├── ml/                           # ML pipeline
│   ├── run_pipeline.py           # Pipeline entry point
│   ├── esg/esg_scoring.py        # ESG scoring logic
│   ├── training/                 # Model training
│   └── preprocessing/            # Data preprocessing
├── Test_Files/                   # Test data samples
├── requirements.txt              # Backend dependencies
└── .vscode/tasks.json            # VS Code tasks
```

---

## 📝 Available VS Code Tasks

Open Command Palette (`Cmd+Shift+P`) and type "Tasks: Run Task" to see all available tasks:

- **Start Backend Server** - Run FastAPI with auto-reload
- **Start Frontend Server** - Run React dev server
- **Run ML Pipeline** - Execute ML model training
- **Install Backend Dependencies** - Update Python packages
- **Install Frontend Dependencies** - Update npm packages

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Kill process on port 8000 (backend)
lsof -ti:8000 | xargs kill -9

# Kill process on port 3000 (frontend)
lsof -ti:3000 | xargs kill -9
```

### Python Module Not Found
```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Reinstall dependencies
.venv/bin/pip install -r requirements.txt
```

### Node Modules Issues
```bash
# Clear npm cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### AWS S3 Access Issues
- Ensure AWS credentials are configured: `~/.aws/credentials`
- Or use IAM role if running on AWS EC2
- Verify `S3_BUCKET_NAME` in config/environment

---

## 🎯 Next Steps

1. **Verify Backend** - Visit `http://localhost:8000/docs`
2. **Test Frontend** - Visit `http://localhost:3000`
3. **Try Analysis** - Use the vessel analysis form
4. **Check Logs** - Monitor terminal output for any issues

---

## 📚 Documentation

- FastAPI Docs: https://fastapi.tiangolo.com/
- React Docs: https://react.dev/
- Tailwind CSS: https://tailwindcss.com/
- AWS SDK: https://boto3.amazonaws.com/

---

## ✨ Ready to Go!

Your Maritime ESG Analytics Platform is fully set up and ready to run. Start the backend and frontend servers and begin analyzing vessel ESG scores!

