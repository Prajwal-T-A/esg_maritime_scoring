# Frontend Quick Start Guide

## 🚀 Get Running in 3 Minutes

### Step 1: Install Dependencies

```bash
cd frontend
npm install
```

This installs:
- React and React DOM
- React Router for navigation
- Axios for API calls
- Tailwind CSS for styling

### Step 2: Verify Backend is Running

Make sure your FastAPI backend is running on port 8000:

```bash
# In the project root directory (not frontend/)
cd /Users/prajwal_t_a/Desktop/Coding/ESG_Scoring_Pipeline
source venv/bin/activate
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Step 3: Start React Development Server

```bash
# In the frontend directory
npm start
```

Browser will automatically open at: `http://localhost:3000`

## ✅ Verify It's Working

1. **Check health indicator** (top of page)
   - Green dot = ✅ Backend connected
   - Red dot = ❌ Backend not running

2. **Test with sample MMSI**
   ```
   Enter MMSI: 419001234
   Click "Latest Data"
   ```

3. **You should see:**
   - Vessel location and speed
   - CO₂ emissions
   - ESG environmental score

## 🎯 What Each Button Does

| Button | What it Shows |
|--------|--------------|
| **Latest Data** | Most recent vessel record + ESG card |
| **History** | All historical records in table format |
| **ESG Metrics** | Only the ESG score card (large view) |

## 🐛 Common Issues

### "Backend is not responding"
```bash
# Make sure backend is running
cd /Users/prajwal_t_a/Desktop/Coding/ESG_Scoring_Pipeline
source venv/bin/activate
uvicorn app.main:app --reload
```

### "No data found for MMSI"
- The MMSI doesn't exist in your S3 data
- Try a different MMSI
- Check S3 bucket has processed files

### Port 3000 already in use
```bash
# Use different port
PORT=3001 npm start
```

### Dependencies won't install
```bash
# Clear and reinstall
rm -rf node_modules package-lock.json
npm install
```

## 📊 Test Data

If you need sample MMSIs, check the Test_Files folder:

```bash
cd /Users/prajwal_t_a/Desktop/Coding/ESG_Scoring_Pipeline/Test_Files
cat ais_sample_001.json | grep mmsi
```

## 🎓 For Viva Demonstration

### Show These Features:

1. **Health Check**
   - Point to green indicator
   - Explain it pings `/api/v1/health`

2. **Latest Data Fetch**
   - Enter MMSI
   - Show both data panels (vessel info + ESG card)
   - Explain color coding

3. **History Table**
   - Click "History" button
   - Show sortable table
   - Point out average calculations

4. **ESG Score Card**
   - Click "ESG Metrics"
   - Explain color scheme:
     - Green (80+) = Excellent
     - Orange (60-79) = Moderate
     - Red (<60) = Poor

### Code to Explain:

**API Service** (`src/services/api.js`):
- Centralized API calls
- Error handling
- Axios configuration

**State Management** (in `Home.js`):
```js
const [mmsi, setMmsi] = useState('');
const [latestData, setLatestData] = useState(null);
```

**Component Structure**:
- Small, reusable components
- Props for data passing
- Clean separation of concerns

## 🔗 Useful URLs

- **Frontend**: http://localhost:3000
- **Backend API Docs**: http://127.0.0.1:8000/docs
- **Backend Health**: http://127.0.0.1:8000/api/v1/health

## 📁 Project Structure Overview

```
frontend/
├── src/
│   ├── components/      ← Reusable UI pieces
│   ├── pages/          ← Full page layouts
│   ├── services/       ← API calls
│   └── App.js          ← Main app + routing
├── public/             ← HTML template
└── package.json        ← Dependencies
```

## 🎨 Tailwind CSS Classes Used

Common classes in the project:
- `bg-blue-600` = Background color
- `text-white` = Text color
- `rounded-lg` = Rounded corners
- `p-6` = Padding
- `flex` = Flexbox layout
- `grid` = Grid layout

## 🔄 Development Workflow

1. Backend running on port 8000
2. Frontend running on port 3000
3. Make changes to `.js` files
4. Browser auto-refreshes
5. Check console for errors

## ✨ Next Steps

Once it's working:
1. Try different MMSIs
2. View history data
3. Compare ESG scores
4. Customize colors in `tailwind.config.js`
5. Add your own components

---

**Ready for your viva? You've got this! 🚀**
