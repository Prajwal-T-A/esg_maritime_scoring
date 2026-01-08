# Quick Start Guide - Maritime ESG Analytics Backend

## 🚀 Getting Started in 5 Minutes

### Step 1: Install Dependencies

```bash
# Navigate to project directory
cd /Users/prajwal_t_a/Desktop/Coding/ESG_Scoring_Pipeline

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure AWS Credentials

Make sure you have AWS credentials configured. Choose one method:

**Option A - AWS CLI (Recommended):**
```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter region: us-east-1
```

**Option B - Environment Variables:**
```bash
export AWS_ACCESS_KEY_ID=your_access_key_here
export AWS_SECRET_ACCESS_KEY=your_secret_key_here
export AWS_REGION=us-east-1
```

### Step 3: Start the Server

```bash
uvicorn app.main:app --reload
```

The server will start at: `http://localhost:8000`

### Step 4: Test the API

**Option A - Browser:**
- Open `http://localhost:8000/docs` for interactive Swagger UI
- Try the `/api/v1/health` endpoint

**Option B - Command Line:**
```bash
# Test health endpoint
curl http://localhost:8000/api/v1/health

# Test with a real MMSI (replace 123456789 with actual MMSI)
curl http://localhost:8000/api/v1/vessels/123456789/latest
curl http://localhost:8000/api/v1/vessels/123456789/history
curl http://localhost:8000/api/v1/esg/123456789
```

**Option C - Python Test Script:**
```bash
# In a new terminal (keep the server running)
python test_api.py
```

## 📋 Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/vessels/{mmsi}/latest` | Latest vessel data |
| GET | `/api/v1/vessels/{mmsi}/history` | Full vessel history |
| GET | `/api/v1/esg/{mmsi}` | ESG metrics only |

## 🔍 Example Usage with React

```javascript
// Fetch latest vessel data
const response = await fetch('http://localhost:8000/api/v1/vessels/123456789/latest');
const data = await response.json();
console.log(data);

// Expected response:
// {
//   "mmsi": "123456789",
//   "speed_knots": 12.5,
//   "latitude": 37.7749,
//   "longitude": -122.4194,
//   "timestamp": "2026-01-08T10:30:00Z",
//   "estimated_co2_kg": 145.3,
//   "esg_environment_score": 75
// }
```

## 🛠 Troubleshooting

### Problem: "AWS credentials not found"
**Solution:** Run `aws configure` or set environment variables

### Problem: "No data found for MMSI"
**Solution:** 
1. Check if data exists in S3: `s3://ai-carbon-esg-data-prajwal/processed/features/`
2. Verify the MMSI is correct
3. Check S3 bucket permissions

### Problem: Port 8000 already in use
**Solution:** Use a different port:
```bash
uvicorn app.main:app --reload --port 8001
```

## 📚 Next Steps

1. **Test with real data:** Use actual MMSI values from your S3 bucket
2. **Integrate with React:** Point your frontend to `http://localhost:8000`
3. **Review API docs:** Visit `http://localhost:8000/docs` for full API documentation
4. **Customize:** Modify [app/config.py](app/config.py) for your specific needs

## 🔗 Useful Links

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Root endpoint:** http://localhost:8000/

## 📞 Need Help?

Check the main [README.md](README.md) for detailed documentation.
