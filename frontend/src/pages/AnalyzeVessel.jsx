/**
 * Analyze Vessel Page Component
 * Main vessel analysis interface with form input and comprehensive results display
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import apiService from '../services/api';
import maritimeBackground from '../images/maritime-operations-data-analysis.avif';
import MarkdownRenderer from '../components/MarkdownRenderer';

function AnalyzeVessel() {
  const navigate = useNavigate();
  
  // Form state
  const [formData, setFormData] = useState({
    mmsi: '',
    avg_speed: '',
    speed_std: '',
    total_distance_km: '',
    time_at_sea_hours: '',
    acceleration_events: '',
    length: '',
    width: '',
    draft: '',
    co2_factor: '3.206' // Default CO2 factor
  });

  // UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  /**
   * Handle form input changes
   */
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  /**
   * Handle form submission
   */
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    // Validate all fields are filled
    const requiredFields = ['mmsi', 'avg_speed', 'speed_std', 'total_distance_km', 
                           'time_at_sea_hours', 'acceleration_events', 'length', 
                           'width', 'draft', 'co2_factor'];
    
    for (const field of requiredFields) {
      if (!formData[field] || formData[field] === '') {
        setError(`Please fill in the ${field.replace(/_/g, ' ')} field`);
        setLoading(false);
        return;
      }
    }

    // Convert string inputs to numbers
    const payload = {
      mmsi: formData.mmsi.trim(),
      avg_speed: parseFloat(formData.avg_speed),
      speed_std: parseFloat(formData.speed_std),
      total_distance_km: parseFloat(formData.total_distance_km),
      time_at_sea_hours: parseFloat(formData.time_at_sea_hours),
      acceleration_events: parseInt(formData.acceleration_events, 10),
      length: parseFloat(formData.length),
      width: parseFloat(formData.width),
      draft: parseFloat(formData.draft),
      co2_factor: parseFloat(formData.co2_factor)
    };

    // Validate no NaN values
    const hasNaN = Object.entries(payload).some(([key, value]) => {
      if (key === 'mmsi') return false;
      return isNaN(value);
    });

    if (hasNaN) {
      setError('Please ensure all numeric fields contain valid numbers');
      setLoading(false);
      return;
    }

    console.log('Sending payload:', payload);

    // Call API
    const response = await apiService.analyzeVessel(payload);

    if (response.success) {
      setResult(response.data);
    } else {
      setError(response.error);
    }

    setLoading(false);
  };

  /**
   * Reset form
   */
  const handleReset = () => {
    setFormData({
      mmsi: '',
      avg_speed: '',
      speed_std: '',
      total_distance_km: '',
      time_at_sea_hours: '',
      acceleration_events: '',
      length: '',
      width: '',
      draft: '',
      co2_factor: '3.206'
    });
    setResult(null);
    setError(null);
  };

  /**
   * Get color for ESG score
   */
  const getScoreColor = (score) => {
    if (score >= 90) return 'text-green-400';
    if (score >= 70) return 'text-lime-400';
    if (score >= 50) return 'text-yellow-400';
    if (score >= 30) return 'text-orange-400';
    return 'text-red-400';
  };

  /**
   * ESG Score Gauge Component
   */
  const ESGGauge = ({ score }) => {
    const percentage = score;
    const rotation = (percentage / 100) * 180 - 90;

    return (
      <div className="relative w-64 h-32 mx-auto">
        {/* Semi-circle background */}
        <svg className="w-full h-full" viewBox="0 0 200 100">
          {/* Background arc */}
          <path
            d="M 10 100 A 90 90 0 0 1 190 100"
            fill="none"
            stroke="#e5e7eb"
            strokeWidth="20"
          />
          {/* Colored arc based on score */}
          <path
            d="M 10 100 A 90 90 0 0 1 190 100"
            fill="none"
            stroke={score >= 90 ? '#10b981' : score >= 70 ? '#84cc16' : score >= 50 ? '#eab308' : score >= 30 ? '#f97316' : '#ef4444'}
            strokeWidth="20"
            strokeDasharray={`${percentage * 2.83} 283`}
            strokeLinecap="round"
          />
          {/* Needle */}
          <line
            x1="100"
            y1="100"
            x2="100"
            y2="20"
            stroke="#1f2937"
            strokeWidth="2"
            transform={`rotate(${rotation} 100 100)`}
          />
          {/* Center dot */}
          <circle cx="100" cy="100" r="5" fill="#1f2937" />
        </svg>
        
        {/* Score display */}
        <div className="absolute inset-0 flex items-end justify-center pb-2">
          <div className="text-center">
            <div className={`text-4xl font-bold ${getScoreColor(score)}`}>
              {score}
            </div>
            <div className="text-xs text-gray-300 uppercase tracking-wide">
              ESG Score
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="relative min-h-screen overflow-hidden">
      {/* Background Image with Overlay */}
      <div 
        className="fixed inset-0 bg-cover bg-center bg-no-repeat"
        style={{ backgroundImage: `url(${maritimeBackground})` }}
      >
        <div className="absolute inset-0 bg-gradient-to-br from-slate-900/85 via-blue-900/75 to-slate-900/85"></div>
      </div>

      {/* Content */}
      <div className="relative z-10 min-h-screen">
        {/* Header */}
        <header className="bg-white/5 border-b border-white/20">
          <div className="max-w-7xl mx-auto px-6 py-4">
            <div className="flex justify-between items-center">
              <div className="flex items-center space-x-3">
                <button
                  onClick={() => navigate('/')}
                  className="text-white hover:text-blue-200 transition-colors font-medium"
                >
                  ← Back
                </button>
                <div className="w-px h-6 bg-white/30"></div>
                <h1 className="text-2xl font-bold text-white tracking-tight">
                  Vessel Analysis
                </h1>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-6 py-8">
          <div className="grid lg:grid-cols-2 gap-8">
            {/* Left Column: Input Form */}
            <div className="bg-white/10 backdrop-blur-md rounded-2xl shadow-2xl border border-white/30 p-8">
              <h2 className="text-2xl font-bold text-white mb-6">
                Vessel Information
              </h2>

            <form onSubmit={handleSubmit} className="space-y-5">
              {/* MMSI */}
              <div>
                <label className="block text-sm font-semibold text-white mb-2">
                  MMSI <span className="text-red-400">*</span>
                </label>
                <input
                  type="text"
                  name="mmsi"
                  value={formData.mmsi}
                  onChange={handleChange}
                  required
                  placeholder="e.g., 316001819"
                  className="w-full px-4 py-3 bg-white/20 border border-white/30 text-white placeholder-white/50 rounded-lg focus:ring-2 focus:ring-cyan-400 focus:border-transparent transition-all"
                />
              </div>

              {/* Speed Metrics */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-white mb-2">
                    Avg Speed (knots) <span className="text-red-400">*</span>
                    <span className="text-xs text-blue-300 ml-2">(0-50)</span>
                  </label>
                  <input
                    type="number"
                    name="avg_speed"
                    value={formData.avg_speed}
                    onChange={handleChange}
                    required
                    min="0"
                    max="50"
                    step="0.01"
                    placeholder="19.75"
                    className="w-full px-4 py-3 bg-white/20 border border-white/30 text-white placeholder-white/50 rounded-lg focus:ring-2 focus:ring-cyan-400 focus:border-transparent transition-all"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-white mb-2">
                    Speed Std Dev <span className="text-red-400">*</span>
                    <span className="text-xs text-blue-300 ml-2">(0-20)</span>
                  </label>
                  <input
                    type="number"
                    name="speed_std"
                    value={formData.speed_std}
                    onChange={handleChange}
                    required
                    min="0"
                    max="20"
                    step="0.01"
                    placeholder="1.8"
                    className="w-full px-4 py-3 bg-white/20 border border-white/30 text-white placeholder-white/50 rounded-lg focus:ring-2 focus:ring-cyan-400 focus:border-transparent transition-all"
                  />
                </div>
              </div>

              {/* Distance & Time */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-white mb-2">
                    Distance (km) <span className="text-red-400">*</span>
                  </label>
                  <input
                    type="number"
                    name="total_distance_km"
                    value={formData.total_distance_km}
                    onChange={handleChange}
                    required
                    min="0"
                    step="0.01"
                    placeholder="87.87"
                    className="w-full px-4 py-3 bg-white/20 border border-white/30 text-white placeholder-white/50 rounded-lg focus:ring-2 focus:ring-cyan-400 focus:border-transparent transition-all"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-white mb-2">
                    Time at Sea (hours) <span className="text-red-400">*</span>
                  </label>
                  <input
                    type="number"
                    name="time_at_sea_hours"
                    value={formData.time_at_sea_hours}
                    onChange={handleChange}
                    required
                    min="0"
                    step="0.01"
                    placeholder="40"
                    className="w-full px-4 py-3 bg-white/20 border border-white/30 text-white placeholder-white/50 rounded-lg focus:ring-2 focus:ring-cyan-400 focus:border-transparent transition-all"
                  />
                </div>
              </div>

              {/* Acceleration Events */}
              <div>
                <label className="block text-sm font-semibold text-white mb-2">
                  Acceleration Events <span className="text-red-400">*</span>
                </label>
                <input
                  type="number"
                  name="acceleration_events"
                  value={formData.acceleration_events}
                  onChange={handleChange}
                  required
                  min="0"
                  placeholder="30"
                  className="w-full px-4 py-3 bg-white/20 border border-white/30 text-white placeholder-white/50 rounded-lg focus:ring-2 focus:ring-cyan-400 focus:border-transparent transition-all"
                />
              </div>

              {/* Vessel Dimensions */}
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-white mb-2">
                    Length (m) <span className="text-red-400">*</span>
                    <span className="text-xs text-blue-300 ml-1">(0-500)</span>
                  </label>
                  <input
                    type="number"
                    name="length"
                    value={formData.length}
                    onChange={handleChange}
                    required
                    min="0"
                    max="500"
                    step="0.01"
                    placeholder="120"
                    className="w-full px-4 py-3 bg-white/20 border border-white/30 text-white placeholder-white/50 rounded-lg focus:ring-2 focus:ring-cyan-400 focus:border-transparent transition-all"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-white mb-2">
                    Width (m) <span className="text-red-400">*</span>
                    <span className="text-xs text-blue-300 ml-1">(0-100)</span>
                  </label>
                  <input
                    type="number"
                    name="width"
                    value={formData.width}
                    onChange={handleChange}
                    required
                    min="0"
                    max="100"
                    step="0.01"
                    placeholder="20"
                    className="w-full px-4 py-3 bg-white/20 border border-white/30 text-white placeholder-white/50 rounded-lg focus:ring-2 focus:ring-cyan-400 focus:border-transparent transition-all"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-white mb-2">
                    Draft (m) <span className="text-red-400">*</span>
                    <span className="text-xs text-blue-300 ml-1">(0-50)</span>
                  </label>
                  <input
                    type="number"
                    name="draft"
                    value={formData.draft}
                    onChange={handleChange}
                    required
                    min="0"
                    max="50"
                    step="0.01"
                    placeholder="7"
                    className="w-full px-4 py-3 bg-white/20 border border-white/30 text-white placeholder-white/50 rounded-lg focus:ring-2 focus:ring-cyan-400 focus:border-transparent transition-all"
                  />
                </div>
              </div>

              {/* CO2 Factor */}
              <div>
                <label className="block text-sm font-semibold text-white mb-2">
                  CO₂ Factor (kg/fuel unit) <span className="text-red-400">*</span>
                  <span className="text-xs text-blue-300 ml-2">(0-10)</span>
                </label>
                <input
                  type="number"
                  name="co2_factor"
                  value={formData.co2_factor}
                  onChange={handleChange}
                  required
                  min="0"
                  max="10"
                  step="0.001"
                  placeholder="3.206"
                  className="w-full px-4 py-3 bg-white/20 border border-white/30 text-white placeholder-white/50 rounded-lg focus:ring-2 focus:ring-cyan-400 focus:border-transparent transition-all"
                />
                <p className="text-xs text-blue-200 mt-1">
                  Default: 3.206 (typical for marine diesel)
                </p>
              </div>

              {/* Buttons */}
              <div className="flex gap-4 pt-4">
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 py-3 bg-gradient-to-r from-cyan-500 to-blue-500 text-white rounded-lg font-semibold hover:from-cyan-400 hover:to-blue-400 disabled:from-gray-500 disabled:to-gray-600 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-cyan-500/50"
                >
                  {loading ? (
                    <span className="flex items-center justify-center">
                      <svg className="animate-spin h-5 w-5 mr-2" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      Analyzing...
                    </span>
                  ) : (
                    'Analyze Vessel'
                  )}
                </button>
                <button
                  type="button"
                  onClick={handleReset}
                  className="px-6 py-3 bg-white/10 border-2 border-white/30 text-white rounded-lg font-semibold hover:bg-white/20 transition-all"
                >
                  Reset
                </button>
              </div>
            </form>
            </div>

            {/* Right Column: Results */}
            <div className="space-y-6">
              {/* Error Display */}
              {error && (
                <div className="bg-red-500/20 backdrop-blur-md border-2 border-red-400/50 rounded-2xl p-6">
                  <div className="flex items-start">
                    <div>
                      <h3 className="font-bold text-white mb-1">Analysis Failed</h3>
                      <p className="text-red-200 text-sm">{error}</p>
                    </div>
                  </div>
                </div>
              )}

            {/* Results Display */}
            {result && (
              <>
                {/* KPI Cards */}
                <div className="grid grid-cols-2 gap-4">
                  {/* CO2 Emissions */}
                  <div className="bg-gradient-to-br from-cyan-500 to-blue-500 backdrop-blur-md rounded-2xl p-6 text-white shadow-2xl border border-white/20">
                    <div className="text-sm font-medium opacity-90 mb-2">
                      Predicted CO₂ Emissions
                    </div>
                    <div className="text-3xl font-bold">
                      {result.estimated_co2_kg.toLocaleString(undefined, {
                        maximumFractionDigits: 2
                      })}
                    </div>
                    <div className="text-sm opacity-90 mt-1">
                      kilograms
                    </div>
                  </div>

                  {/* ESG Score */}
                  <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 shadow-2xl border-2 border-white/30">
                    <div className="text-sm font-medium text-white mb-2">
                      ESG Score
                    </div>
                    <div className={`text-3xl font-bold ${getScoreColor(result.esg_score)}`}>
                      {result.esg_score}/100
                    </div>
                    <div className="text-sm text-blue-200 mt-1">
                      {result.rating}
                    </div>
                  </div>
                </div>

                {/* ESG Gauge */}
                <div className="bg-white/10 backdrop-blur-md rounded-2xl shadow-2xl border border-white/30 p-8">
                  <h3 className="text-xl font-bold text-white mb-6 text-center">
                    Environmental Performance
                  </h3>
                  <ESGGauge score={result.esg_score} />
                  <div className="mt-6 text-center">
                    <p className="text-blue-100 text-sm">
                      {result.description}
                    </p>
                  </div>
                </div>

                {/* Recommendation Panel */}
                <div className="bg-gradient-to-br from-purple-500/20 to-pink-500/20 backdrop-blur-md rounded-2xl shadow-2xl border-2 border-purple-400/30 p-6">
                  <div>
                    <h3 className="font-bold text-white mb-3 text-lg">
                      AI-Powered Recommendations
                    </h3>
                    <div className="text-blue-100">
                      <MarkdownRenderer content={result.recommendation} />
                    </div>
                  </div>
                </div>

                {/* Risk Flags */}
                {result.risk_flags && result.risk_flags.length > 0 && (
                  <div className="bg-red-500/10 backdrop-blur-md rounded-2xl shadow-2xl border border-red-400/40 p-6">
                    <h3 className="font-bold text-white mb-4">
                      Environmental Risk Flags
                    </h3>
                    <div className="space-y-2">
                      {result.risk_flags.map((flag, index) => (
                        <div
                          key={index}
                          className="bg-red-500/20 border-l-4 border-red-400 p-3 rounded backdrop-blur-sm"
                        >
                          <p className="text-red-100 text-sm font-medium">
                            {flag}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* No Risk Flags */}
                {result.risk_flags && result.risk_flags.length === 0 && (
                  <div className="bg-green-500/20 backdrop-blur-md border-2 border-green-400/30 rounded-2xl p-6">
                    <div>
                      <h3 className="font-bold text-white">
                        No Environmental Risks Detected
                      </h3>
                      <p className="text-green-100 text-sm mt-1">
                        Vessel operating within optimal environmental parameters
                      </p>
                    </div>
                  </div>
                )}
              </>
            )}

            {/* Placeholder when no results */}
            {!result && !error && (
              <div className="bg-white/10 backdrop-blur-md rounded-2xl shadow-2xl border border-white/30 p-12 text-center">
                <h3 className="text-xl font-semibold text-white mb-2">
                  Ready to Analyze
                </h3>
                <p className="text-blue-200">
                  Fill in the vessel information and click "Analyze Vessel" to see results
                </p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  </div>
  );
}

export default AnalyzeVessel;
