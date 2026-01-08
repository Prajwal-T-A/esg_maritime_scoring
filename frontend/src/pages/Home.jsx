/**
 * Home Page Component
 * Main page of the application
 * 
 * Features:
 * - MMSI input field
 * - Fetch buttons for different data types
 * - Display vessel data, history, and ESG metrics
 */

import React, { useState } from 'react';
import HealthStatus from '../components/HealthStatus.jsx';
import VesselLatest from '../components/VesselLatest.jsx';
import VesselHistory from '../components/VesselHistory.jsx';
import ESGScoreCard from '../components/ESGScoreCard.jsx';
import apiService from '../services/api';

function Home() {
  // State management using React hooks
  const [mmsi, setMmsi] = useState(''); // User input
  const [latestData, setLatestData] = useState(null); // Latest vessel data
  const [historyData, setHistoryData] = useState(null); // Historical data
  const [esgData, setEsgData] = useState(null); // ESG metrics
  const [loading, setLoading] = useState(false); // Loading state
  const [error, setError] = useState(null); // Error messages
  const [activeView, setActiveView] = useState('latest'); // Which view is active

  /**
   * Fetch latest vessel data from backend
   */
  const handleFetchLatest = async () => {
    // Validate MMSI input
    if (!mmsi.trim()) {
      setError('Please enter a valid MMSI');
      return;
    }

    setLoading(true);
    setError(null);
    setActiveView('latest');

    // Call API service
    const result = await apiService.getVesselLatest(mmsi.trim());

    if (result.success) {
      setLatestData(result.data);
    } else {
      setError(result.error);
      setLatestData(null);
    }

    setLoading(false);
  };

  /**
   * Fetch vessel history from backend
   */
  const handleFetchHistory = async () => {
    if (!mmsi.trim()) {
      setError('Please enter a valid MMSI');
      return;
    }

    setLoading(true);
    setError(null);
    setActiveView('history');

    const result = await apiService.getVesselHistory(mmsi.trim());

    if (result.success) {
      setHistoryData(result.data);
    } else {
      setError(result.error);
      setHistoryData(null);
    }

    setLoading(false);
  };

  /**
   * Fetch ESG metrics from backend
   */
  const handleFetchESG = async () => {
    if (!mmsi.trim()) {
      setError('Please enter a valid MMSI');
      return;
    }

    setLoading(true);
    setError(null);
    setActiveView('esg');

    const result = await apiService.getESGMetrics(mmsi.trim());

    if (result.success) {
      setEsgData(result.data);
    } else {
      setError(result.error);
      setEsgData(null);
    }

    setLoading(false);
  };

  /**
   * Handle Enter key press in input field
   */
  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleFetchLatest();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-800">
            🚢 Maritime ESG Analytics
          </h1>
          <p className="text-gray-600 mt-2">
            Track carbon emissions and environmental scores for maritime vessels
          </p>
          
          {/* Backend Health Status */}
          <div className="mt-4">
            <HealthStatus />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Input Section */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">
            Enter Vessel MMSI
          </h2>
          
          <div className="flex flex-col md:flex-row gap-4">
            {/* MMSI Input */}
            <input
              type="text"
              value={mmsi}
              onChange={(e) => setMmsi(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="e.g., 419001234"
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-lg"
            />

            {/* Action Buttons */}
            <div className="flex gap-2">
              <button
                onClick={handleFetchLatest}
                disabled={loading}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-semibold"
              >
                Latest Data
              </button>

              <button
                onClick={handleFetchHistory}
                disabled={loading}
                className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-semibold"
              >
                History
              </button>

              <button
                onClick={handleFetchESG}
                disabled={loading}
                className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-semibold"
              >
                ESG Metrics
              </button>
            </div>
          </div>

          {/* Instructions */}
          <p className="text-sm text-gray-500 mt-3">
            Enter a Maritime Mobile Service Identity (MMSI) to view vessel data from AWS S3
          </p>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-800 font-semibold">Error</p>
            <p className="text-red-600 text-sm mt-1">{error}</p>
          </div>
        )}

        {/* Loading Indicator */}
        {loading && (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600"></div>
            <p className="ml-4 text-gray-600 text-lg">Loading data...</p>
          </div>
        )}

        {/* Data Display - Latest View */}
        {!loading && activeView === 'latest' && latestData && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Vessel Latest Data - Takes 2 columns */}
            <div className="lg:col-span-2">
              <VesselLatest data={latestData} />
            </div>

            {/* ESG Score Card - Takes 1 column */}
            <div>
              <ESGScoreCard
                score={latestData.esg_environment_score}
                co2Emissions={latestData.estimated_co2_kg}
                timestamp={latestData.timestamp}
              />
            </div>
          </div>
        )}

        {/* Data Display - History View */}
        {!loading && activeView === 'history' && historyData && (
          <VesselHistory data={historyData} loading={loading} />
        )}

        {/* Data Display - ESG View */}
        {!loading && activeView === 'esg' && esgData && (
          <div className="max-w-md mx-auto">
            <ESGScoreCard
              score={esgData.esg_environment_score}
              co2Emissions={esgData.estimated_co2_kg}
              timestamp={esgData.timestamp}
            />
          </div>
        )}

        {/* Welcome Message - Show when no data loaded */}
        {!loading && !latestData && !historyData && !esgData && !error && (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🌊</div>
            <h2 className="text-2xl font-semibold text-gray-700 mb-2">
              Welcome to Maritime ESG Analytics
            </h2>
            <p className="text-gray-500">
              Enter a vessel MMSI above to get started
            </p>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 py-6 text-center text-gray-600 text-sm">
          <p>Maritime ESG Analytics Dashboard</p>
          <p className="mt-1">
            Backend: FastAPI | Frontend: React.js | Data: AWS S3
          </p>
        </div>
      </footer>
    </div>
  );
}

export default Home;
