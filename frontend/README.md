# Maritime ESG Analytics - React Frontend

React.js frontend for the Maritime ESG Analytics dashboard. Displays vessel carbon emissions and ESG environmental scores by consuming FastAPI backend.

## 🎯 Project Overview

This is the frontend component of a full-stack sustainability analytics project for maritime freight. It provides a clean, intuitive interface for:

- Viewing real-time vessel AIS data
- Tracking carbon emissions (CO₂)
- Monitoring ESG environmental scores
- Analyzing historical vessel performance

## 🏗️ Architecture

```
Frontend (React.js) → Backend (FastAPI) → Data Source (AWS S3)
```

- **Frontend**: React.js + Tailwind CSS
- **Backend**: FastAPI (Python)
- **Data**: Processed AIS records from AWS S3

## 📁 Project Structure

```
frontend/
├── public/
│   └── index.html          # HTML template
├── src/
│   ├── components/         # Reusable UI components
│   │   ├── HealthStatus.js     # Backend health indicator
│   │   ├── VesselLatest.js     # Latest vessel data display
│   │   ├── VesselHistory.js    # Historical data table
│   │   └── ESGScoreCard.js     # ESG score visualization
│   ├── pages/
│   │   └── Home.js             # Main application page
│   ├── services/
│   │   └── api.js              # API service layer (all backend calls)
│   ├── App.js                  # Main app with routing
│   ├── index.js                # React entry point
│   └── index.css               # Global styles + Tailwind
├── package.json            # Dependencies
├── tailwind.config.js      # Tailwind configuration
└── .env                    # Environment variables
```

## 🚀 Quick Start

### Prerequisites

- Node.js 16+ and npm
- Backend FastAPI server running on `http://127.0.0.1:8000`

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

The app will open at: `http://localhost:3000`

### Verify Backend Connection

1. Check the health indicator in the top header
2. Green dot = Backend connected ✅
3. Red dot = Backend not responding ❌

## 🎨 Features

### 1. Health Status Indicator
- Real-time backend connectivity check
- Visual indicator (green/red/yellow)
- Refresh button to recheck

### 2. Vessel Latest Data
- Display most recent AIS record
- Shows location (lat/lon), speed, timestamp
- Highlights CO₂ emissions and ESG score

### 3. Vessel History
- Sortable table of historical records
- Timestamp-based sorting
- Color-coded ESG scores
- Average calculations in footer

### 4. ESG Score Card
- Visual score display (0-100)
- Color coding:
  - **Green (80-100)**: Excellent performance
  - **Orange (60-79)**: Moderate performance
  - **Red (<60)**: Needs improvement
- CO₂ emissions display
- Score interpretation guide

## 🔌 API Integration

The frontend connects to 4 backend endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/health` | GET | Check backend status |
| `/api/v1/vessels/{mmsi}/latest` | GET | Get latest vessel data |
| `/api/v1/vessels/{mmsi}/history` | GET | Get vessel history |
| `/api/v1/esg/{mmsi}` | GET | Get ESG metrics only |

All API calls are centralized in `src/services/api.js` for easy maintenance.

## ⚙️ Configuration

### Environment Variables

Edit `.env` file to configure backend URL:

```env
REACT_APP_API_BASE_URL=http://127.0.0.1:8000
```

### Tailwind CSS

Custom theme colors defined in `tailwind.config.js`:

```js
colors: {
  'esg-green': '#10b981',   // Score >= 80
  'esg-orange': '#f59e0b',  // Score 60-79
  'esg-red': '#ef4444',     // Score < 60
}
```

## 📖 Usage Guide

### Step 1: Enter MMSI
Enter a vessel's Maritime Mobile Service Identity (MMSI) in the input field.

Example MMSIs from test data:
- `419001234`
- `367123456`
- `538001234`

### Step 2: Fetch Data
Click one of three buttons:

1. **Latest Data**: Shows most recent vessel record + ESG card
2. **History**: Displays all historical records in a table
3. **ESG Metrics**: Shows only ESG score card

### Step 3: View Results
- Latest data appears in a two-column layout
- History displays as a scrollable table
- ESG metrics show large score visualization

### Error Handling
- Empty MMSI → Validation error
- Invalid MMSI → 404 error from backend
- Backend down → Connection error

## 🛠️ Development

### Code Organization

**Components** (`src/components/`):
- Small, reusable UI pieces
- Each has a single responsibility
- Well-commented for viva preparation

**Pages** (`src/pages/`):
- Full page layouts
- Combine multiple components
- Handle data fetching and state

**Services** (`src/services/`):
- API communication logic
- Centralized error handling
- Returns consistent response format

### State Management

Uses React Hooks:
- `useState`: Component state
- `useEffect`: Side effects (API calls, lifecycle)

Example:
```js
const [mmsi, setMmsi] = useState('');           // User input
const [latestData, setLatestData] = useState(null);  // API response
const [loading, setLoading] = useState(false);  // Loading state
```

### Adding New Features

**To add a new API endpoint:**

1. Add function to `src/services/api.js`:
```js
getNewEndpoint: async (param) => {
  const response = await apiClient.get(`/new-endpoint/${param}`);
  return { success: true, data: response.data };
}
```

2. Call from component:
```js
const result = await apiService.getNewEndpoint(param);
```

**To add a new component:**

1. Create file in `src/components/`
2. Follow existing pattern (props, comments)
3. Import and use in page

## 🎓 Viva Preparation Notes

### Key Concepts to Explain

1. **Component-Based Architecture**
   - Each UI piece is a separate component
   - Components are reusable and modular
   - Props pass data from parent to child

2. **State Management**
   - `useState` hook manages component data
   - State changes trigger re-renders
   - Unidirectional data flow

3. **API Integration**
   - Axios handles HTTP requests
   - Centralized in service layer
   - Async/await for cleaner code

4. **Styling**
   - Tailwind CSS utility classes
   - Responsive design (mobile-first)
   - Color-coded ESG scores

5. **Error Handling**
   - Try-catch blocks in API service
   - Error state displayed to user
   - Loading states improve UX

### Data Flow Example

```
User enters MMSI
  ↓
onClick handler triggered
  ↓
State updated (loading = true)
  ↓
API service called
  ↓
FastAPI backend queried
  ↓
S3 data retrieved
  ↓
Response returned to frontend
  ↓
State updated with data
  ↓
Component re-renders
  ↓
UI displays data
```

## 🐛 Troubleshooting

### Issue: "Backend is not responding"
**Solution**: 
1. Ensure FastAPI server is running: `uvicorn app.main:app --reload`
2. Check backend URL in `.env` file
3. Verify CORS is enabled in backend

### Issue: "No data found for MMSI"
**Solution**:
1. Verify MMSI exists in S3 data
2. Check S3 bucket has processed files
3. Try a different MMSI

### Issue: Styling not working
**Solution**:
1. Ensure Tailwind is installed: `npm install tailwindcss`
2. Check `tailwind.config.js` exists
3. Restart dev server: `npm start`

### Issue: Can't install dependencies
**Solution**:
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

## 📊 Sample Data Format

Backend returns data in this format:

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

## 🚢 Deployment

### Build for Production

```bash
npm run build
```

Creates optimized build in `build/` directory.

### Deploy Options

1. **Vercel** (Recommended for React):
   ```bash
   npm install -g vercel
   vercel
   ```

2. **Netlify**:
   - Connect GitHub repository
   - Build command: `npm run build`
   - Publish directory: `build`

3. **AWS S3 + CloudFront**:
   ```bash
   npm run build
   aws s3 sync build/ s3://your-bucket-name
   ```

### Environment Variables in Production

Set `REACT_APP_API_BASE_URL` to your production backend URL.

## 📝 Scripts

```bash
npm start       # Start development server
npm run build   # Build for production
npm test        # Run tests
```

## 🔗 Related Documentation

- Backend API docs: `http://127.0.0.1:8000/docs`
- React documentation: https://react.dev/
- Tailwind CSS: https://tailwindcss.com/

## 📧 Support

For questions or issues during viva:
1. Explain the component structure
2. Walk through the data flow
3. Show how API calls work
4. Demonstrate error handling

## 🎯 Future Enhancements

- [ ] Add vessel search autocomplete
- [ ] Implement data visualization (charts)
- [ ] Add export to CSV functionality
- [ ] Real-time updates with WebSockets
- [ ] User authentication
- [ ] Vessel comparison feature
- [ ] Dark mode theme

## 📄 License

Academic project - Internal use only

---

**Built with React.js for Maritime Sustainability Analytics**
