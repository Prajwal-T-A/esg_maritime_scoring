/**
 * Analyze Vessel Page Component
 * Main vessel analysis interface with form input and comprehensive results display
 */

import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import apiService from '../services/api';
import maritimeBackground from '../images/maritime-operations-data-analysis.avif';
import MarkdownRenderer from '../components/MarkdownRenderer';

function AnalyzeVessel() {
  const navigate = useNavigate();

  // View mode state
  const [viewMode, setViewMode] = useState('single'); // 'single' or 'fleet'

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

  // Fleet analysis state
  const [fleetVessels, setFleetVessels] = useState({});
  const [fleetConnectionStatus, setFleetConnectionStatus] = useState('Disconnected');
  const [selectedPort, setSelectedPort] = useState('all');
  const [fleetReport, setFleetReport] = useState(null);
  const [generatingFleetReport, setGeneratingFleetReport] = useState(false);
  const vesselsRef = useRef({});

  /**
   * WebSocket connection for fleet analysis
   */
  useEffect(() => {
    if (viewMode !== 'fleet') return;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//localhost:8000/api/v1/ws/live-vessels`;

    let ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      setFleetConnectionStatus('Connected');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        vesselsRef.current = {
          ...vesselsRef.current,
          [data.mmsi]: data
        };
        setFleetVessels({ ...vesselsRef.current });
      } catch (e) {
        console.error("Error parsing WS message", e);
      }
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
      setFleetConnectionStatus('Connection Error');
    };

    ws.onclose = () => {
      setFleetConnectionStatus('Disconnected');
    };

    return () => {
      if (ws) ws.close();
    };
  }, [viewMode]);

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
   * Handle Report Generation
   */
  const handleGenerateReport = async () => {
    if (!result) return;

    setLoading(true); // Re-use global loading or add specific one
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
      co2_factor: parseFloat(formData.co2_factor),
      generate_report: true
    };

    const response = await apiService.analyzeVessel(payload);

    if (response.success) {
      setResult(response.data); // Should now include detailed_report
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
   * Handle Fleet Report Generation
   */
  const handleGenerateFleetReport = async () => {
    console.log('Generate Fleet Report button clicked');
    const vesselList = Object.values(fleetVessels);
    console.log('Fleet vessels count:', vesselList.length);
    console.log('Fleet vessels data:', vesselList);
    
    if (vesselList.length === 0) {
      const errorMsg = 'No vessels available to generate report. Please wait for vessels to load from WebSocket.';
      console.error(errorMsg);
      setError(errorMsg);
      return;
    }

    // Transform vessel data to match FleetVesselData schema
    const transformedVessels = vesselList.map(v => ({
      mmsi: v.mmsi,
      vessel_name: v.vessel_name || `Vessel ${v.mmsi}`,
      lat: v.lat,
      lon: v.lon,
      speed: v.speed,
      estimated_co2_kg: v.adjusted_co2 || v.base_co2 || 0,
      esg_score: v.esg_score || 0,
      sector: v.sector,
      total_distance_km: (v.speed || 0) * 1.852, // Convert knots to km (1 hour)
      delta_weather: v.delta_weather || 0
    }));

    console.log('Transformed vessels:', transformedVessels);

    setGeneratingFleetReport(true);
    setError(null);

    try {
      console.log('Calling analyzeFleet API with port:', selectedPort);
      const response = await apiService.analyzeFleet(transformedVessels, selectedPort);
      console.log('Fleet analysis response:', response);

      if (response.success) {
        console.log('Fleet report generated successfully');
        setFleetReport(response.data);
      } else {
        // Convert error to string if it's an object (e.g., Pydantic validation error)
        let errorMsg = 'Failed to generate fleet report';
        if (response.error) {
          if (typeof response.error === 'string') {
            errorMsg = response.error;
          } else if (typeof response.error === 'object') {
            errorMsg = JSON.stringify(response.error, null, 2);
          }
        }
        console.error('Fleet analysis failed:', errorMsg);
        setError(errorMsg);
      }
    } catch (err) {
      const errorMsg = 'Error generating fleet report: ' + err.message;
      console.error('Fleet analysis exception:', err);
      setError(errorMsg);
    } finally {
      setGeneratingFleetReport(false);
    }
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

  /**
   * Fleet Analysis Component
   */
  const FleetAnalysis = () => {
    const vesselList = Object.values(fleetVessels);
    
    // Group vessels by sector/port
    const vesselsBySector = vesselList.reduce((acc, vessel) => {
      const sector = vessel.sector || 'Unknown';
      if (!acc[sector]) acc[sector] = [];
      acc[sector].push(vessel);
      return acc;
    }, {});

    // Get filtered vessels based on selected port
    const filteredVessels = selectedPort === 'all' 
      ? vesselList 
      : vesselsBySector[selectedPort] || [];

    // Calculate aggregate statistics
    const totalEmissions = filteredVessels.reduce((sum, v) => {
      const baseEmission = v.estimated_co2_kg || 0;
      const weatherImpact = v.delta_weather || 0;
      return sum + baseEmission + weatherImpact;
    }, 0);

    const averageESG = filteredVessels.length > 0
      ? filteredVessels.reduce((sum, v) => sum + (v.esg_score || 0), 0) / filteredVessels.length
      : 0;

    // Calculate total distance as speed (knots) * time (1 hour) = nautical miles
    const totalDistance = filteredVessels.reduce((sum, v) => sum + (v.speed || 0), 0);

    return (
      <div className="space-y-6">
        {/* Fleet Header */}
        <div className="bg-white/10 backdrop-blur-md rounded-2xl shadow-2xl border border-white/30 p-6">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h2 className="text-2xl font-bold text-white">Fleet Analysis</h2>
              <p className="text-blue-200 text-sm mt-1">Real-time vessel tracking by port</p>
            </div>
            <div className={`px-4 py-2 rounded-full text-sm font-mono border ${
              fleetConnectionStatus === 'Connected' 
                ? 'bg-green-500/20 border-green-500 text-green-300' 
                : 'bg-red-500/20 border-red-500 text-red-300'
            }`}>
              ● {fleetConnectionStatus}
            </div>
          </div>

          {/* Port Filter */}
          <div className="flex items-center gap-4">
            <label className="text-white font-semibold">Filter by Port:</label>
            <select
              value={selectedPort}
              onChange={(e) => {
                console.log('Port selected:', e.target.value);
                setSelectedPort(e.target.value);
              }}
              className="px-4 py-2 bg-slate-700 border-2 border-cyan-400/50 text-white rounded-lg focus:ring-2 focus:ring-cyan-400 focus:border-cyan-400 hover:border-cyan-400 cursor-pointer font-semibold shadow-lg [&>option]:bg-slate-800 [&>option]:text-white [&>option]:py-2"
            >
              <option value="all" className="bg-slate-800 text-white">✓ All Ports</option>
              {Object.keys(vesselsBySector).sort().map(sector => (
                <option key={sector} value={sector} className="bg-slate-800 text-white">{sector}</option>
              ))}
            </select>
            <span className="text-cyan-400 text-sm font-mono">
              Selected: {selectedPort === 'all' ? 'All Ports' : selectedPort}
            </span>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-500/20 backdrop-blur-md border-2 border-red-400/30 rounded-2xl p-6">
            <div className="flex items-start gap-3">
              <span className="text-2xl">⚠️</span>
              <div>
                <h3 className="font-bold text-red-300 text-lg mb-1">Error</h3>
                <p className="text-red-100">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Aggregate Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-gradient-to-br from-cyan-500 to-blue-500 rounded-xl p-6 text-white shadow-xl">
            <div className="text-sm opacity-90 mb-2">Total Vessels</div>
            <div className="text-3xl font-bold">{filteredVessels.length}</div>
            <div className="text-xs opacity-80 mt-1">
              {selectedPort === 'all' ? 'All Ports' : selectedPort}
            </div>
          </div>

          <div className="bg-gradient-to-br from-red-500 to-orange-500 rounded-xl p-6 text-white shadow-xl">
            <div className="text-sm opacity-90 mb-2">Total CO₂ Emissions</div>
            <div className="text-3xl font-bold">
              {(totalEmissions / 1000).toFixed(1)}
            </div>
            <div className="text-xs opacity-80 mt-1">tonnes</div>
          </div>

          <div className="bg-gradient-to-br from-green-500 to-emerald-500 rounded-xl p-6 text-white shadow-xl">
            <div className="text-sm opacity-90 mb-2">Average ESG Score</div>
            <div className="text-3xl font-bold">{averageESG.toFixed(1)}</div>
            <div className="text-xs opacity-80 mt-1">out of 100</div>
          </div>

          <div className="bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl p-6 text-white shadow-xl">
            <div className="text-sm opacity-90 mb-2">Total Distance</div>
            <div className="text-3xl font-bold">
              {totalDistance.toFixed(1)}
            </div>
            <div className="text-xs opacity-80 mt-1">nautical miles (1 hr)</div>
          </div>
        </div>

        {/* Vessels Table */}
        <div className="bg-white/10 backdrop-blur-md rounded-2xl shadow-2xl border border-white/30 overflow-hidden">
          <div className="p-6 border-b border-white/20">
            <h3 className="text-xl font-bold text-white">Vessel Details</h3>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-white/5 border-b border-white/20">
                <tr>
                  <th className="px-4 py-3 text-left text-white font-semibold">Vessel Name</th>
                  <th className="px-4 py-3 text-left text-white font-semibold">MMSI</th>
                  <th className="px-4 py-3 text-left text-white font-semibold">Latitude</th>
                  <th className="px-4 py-3 text-left text-white font-semibold">Longitude</th>
                  <th className="px-4 py-3 text-left text-white font-semibold">Speed (kts)</th>
                  <th className="px-4 py-3 text-left text-white font-semibold">CO₂ (kg)</th>
                  <th className="px-4 py-3 text-left text-white font-semibold">Weather Impact</th>
                  <th className="px-4 py-3 text-left text-white font-semibold">ESG Score</th>
                  <th className="px-4 py-3 text-left text-white font-semibold">Port/Sector</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/10">
                {filteredVessels.length > 0 ? (
                  filteredVessels.map((vessel) => {
                    const totalCO2 = (vessel.estimated_co2_kg || 0) + (vessel.delta_weather || 0);
                    return (
                      <tr key={vessel.mmsi} className="hover:bg-white/5 transition-colors">
                        <td className="px-4 py-3 text-cyan-300 font-medium">
                          {vessel.vessel_name || 'Unknown'}
                        </td>
                        <td className="px-4 py-3 text-slate-300 font-mono text-xs">
                          {vessel.mmsi}
                        </td>
                        <td className="px-4 py-3 text-slate-300 font-mono">
                          {vessel.lat?.toFixed(6) || 'N/A'}
                        </td>
                        <td className="px-4 py-3 text-slate-300 font-mono">
                          {vessel.lon?.toFixed(6) || 'N/A'}
                        </td>
                        <td className="px-4 py-3 text-slate-300">
                          {vessel.speed?.toFixed(1) || '0.0'}
                        </td>
                        <td className="px-4 py-3 text-orange-300 font-semibold">
                          {totalCO2.toFixed(0)}
                        </td>
                        <td className="px-4 py-3">
                          {vessel.delta_weather > 0 ? (
                            <span className="text-yellow-400 text-xs">
                              +{vessel.delta_weather.toFixed(0)} kg
                            </span>
                          ) : (
                            <span className="text-green-400 text-xs">Nominal</span>
                          )}
                        </td>
                        <td className="px-4 py-3">
                          <span className={`px-2 py-1 rounded text-xs font-bold ${
                            vessel.esg_score >= 90 ? 'bg-green-500/20 text-green-300' :
                            vessel.esg_score >= 70 ? 'bg-blue-500/20 text-blue-300' :
                            vessel.esg_score >= 50 ? 'bg-yellow-500/20 text-yellow-300' :
                            vessel.esg_score >= 30 ? 'bg-orange-500/20 text-orange-300' :
                            'bg-red-500/20 text-red-300'
                          }`}>
                            {vessel.esg_score}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-slate-300 text-xs">
                          {vessel.sector || 'Unknown'}
                        </td>
                      </tr>
                    );
                  })
                ) : (
                  <tr>
                    <td colSpan="9" className="px-4 py-8 text-center text-slate-400">
                      {fleetConnectionStatus === 'Connected' 
                        ? 'Waiting for vessel data...' 
                        : 'Not connected. Please check the connection status.'}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Weather Conditions Summary */}
        {filteredVessels.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-white/10 backdrop-blur-md rounded-xl border border-white/30 p-6">
              <h3 className="text-lg font-bold text-white mb-4">Weather Conditions</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-slate-300">Average Wind Speed:</span>
                  <span className="text-cyan-400 font-mono font-semibold">
                    {(() => {
                      const validVessels = filteredVessels.filter(v => v.weather?.wind_speed_ms);
                      if (validVessels.length === 0) return 'N/A';
                      const avg = validVessels.reduce((sum, v) => sum + v.weather.wind_speed_ms, 0) / validVessels.length;
                      return `${avg.toFixed(1)} m/s`;
                    })()}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-300">Average Wave Height:</span>
                  <span className="text-cyan-400 font-mono font-semibold">
                    {(() => {
                      const validVessels = filteredVessels.filter(v => v.weather?.wave_height_m);
                      if (validVessels.length === 0) return 'N/A';
                      const avg = validVessels.reduce((sum, v) => sum + v.weather.wave_height_m, 0) / validVessels.length;
                      return `${avg.toFixed(1)} m`;
                    })()}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-300">Total Weather Impact:</span>
                  <span className="text-yellow-400 font-mono font-semibold">
                    +{filteredVessels.reduce((sum, v) => sum + (v.delta_weather || 0), 0).toFixed(0)} kg CO₂
                  </span>
                </div>
              </div>
            </div>

            <div className="bg-white/10 backdrop-blur-md rounded-xl border border-white/30 p-6">
              <h3 className="text-lg font-bold text-white mb-4">Fleet Health</h3>
              <div className="space-y-2">
                <div className="flex justify-between items-center p-2 bg-green-500/10 rounded">
                  <span className="text-green-300">Excellent (90+)</span>
                  <span className="text-green-300 font-bold">
                    {filteredVessels.filter(v => v.esg_score >= 90).length}
                  </span>
                </div>
                <div className="flex justify-between items-center p-2 bg-blue-500/10 rounded">
                  <span className="text-blue-300">Good (70-89)</span>
                  <span className="text-blue-300 font-bold">
                    {filteredVessels.filter(v => v.esg_score >= 70 && v.esg_score < 90).length}
                  </span>
                </div>
                <div className="flex justify-between items-center p-2 bg-yellow-500/10 rounded">
                  <span className="text-yellow-300">Moderate (50-69)</span>
                  <span className="text-yellow-300 font-bold">
                    {filteredVessels.filter(v => v.esg_score >= 50 && v.esg_score < 70).length}
                  </span>
                </div>
                <div className="flex justify-between items-center p-2 bg-red-500/10 rounded">
                  <span className="text-red-300">Critical (&lt;50)</span>
                  <span className="text-red-300 font-bold">
                    {filteredVessels.filter(v => v.esg_score < 50).length}
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {/* Fleet Report Section */}
        <div className="mt-6">
          {fleetReport ? (
            <div className="bg-slate-900/50 backdrop-blur-md rounded-2xl shadow-2xl border border-white/20 p-8">
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-2xl font-bold text-white">
                  Comprehensive Fleet Environmental Report
                </h3>
                <div className="flex gap-2">
                  <button
                    onClick={() => window.print()}
                    className="text-sm bg-white/10 hover:bg-white/20 px-4 py-2 rounded-lg text-blue-200 transition-colors"
                  >
                    🖨️ Print / Save PDF
                  </button>
                  <button
                    onClick={() => setFleetReport(null)}
                    className="text-sm bg-red-500/20 hover:bg-red-500/30 px-4 py-2 rounded-lg text-red-200 transition-colors"
                  >
                    ✕ Close Report
                  </button>
                </div>
              </div>
              
              {/* Report Metadata */}
              <div className="grid grid-cols-4 gap-4 mb-6 p-4 bg-white/5 rounded-lg">
                <div className="text-center">
                  <div className="text-sm text-slate-400">Total Vessels</div>
                  <div className="text-2xl font-bold text-cyan-400">{fleetReport.total_vessels}</div>
                </div>
                <div className="text-center">
                  <div className="text-sm text-slate-400">Total Emissions</div>
                  <div className="text-2xl font-bold text-orange-400">
                    {(fleetReport.total_emissions_kg / 1000).toFixed(1)} t
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-sm text-slate-400">Average ESG Score</div>
                  <div className={`text-2xl font-bold ${getScoreColor(fleetReport.average_esg_score)}`}>
                    {fleetReport.average_esg_score.toFixed(1)}
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-sm text-slate-400">Total Distance</div>
                  <div className="text-2xl font-bold text-purple-400">
                    {(fleetReport.total_distance_km / 1.852).toFixed(0)} nm
                  </div>
                </div>
              </div>
              
              {/* Report Content */}
              <div className="prose prose-invert prose-lg max-w-none text-slate-300">
                <MarkdownRenderer content={fleetReport.detailed_report} />
              </div>
            </div>
          ) : (
            <div className="flex justify-center">
              <button
                onClick={handleGenerateFleetReport}
                disabled={generatingFleetReport || Object.keys(fleetVessels).length === 0}
                className="flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-xl font-bold text-lg hover:from-emerald-400 hover:to-teal-400 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-xl hover:shadow-emerald-500/30 transform hover:-translate-y-1"
              >
                {generatingFleetReport ? (
                  <>
                    <svg className="animate-spin h-6 w-6" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Generating Comprehensive Report...
                  </>
                ) : (
                  <>
                    📊 Generate Comprehensive Fleet Report
                  </>
                )}
              </button>
            </div>
          )}
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
              
              {/* View Mode Toggle */}
              <div className="flex gap-2 bg-white/10 rounded-lg p-1">
                <button
                  onClick={() => setViewMode('single')}
                  className={`px-6 py-2 rounded-md font-semibold transition-all ${
                    viewMode === 'single'
                      ? 'bg-gradient-to-r from-cyan-500 to-blue-500 text-white shadow-lg'
                      : 'text-white/70 hover:text-white'
                  }`}
                >
                  Single Vessel
                </button>
                <button
                  onClick={() => setViewMode('fleet')}
                  className={`px-6 py-2 rounded-md font-semibold transition-all ${
                    viewMode === 'fleet'
                      ? 'bg-gradient-to-r from-cyan-500 to-blue-500 text-white shadow-lg'
                      : 'text-white/70 hover:text-white'
                  }`}
                >
                  Fleet Analysis
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-6 py-8">
          {viewMode === 'single' ? (
            // Single Vessel Analysis View
          <>
            {/* Show full-width report if detailed report exists */}
            {result?.detailed_report ? (
              <div className="w-full">
                <div className="bg-slate-900/50 backdrop-blur-md rounded-2xl shadow-2xl border border-white/20 p-8">
                  <div className="flex justify-between items-center mb-6">
                    <h3 className="text-2xl font-bold text-white">
                      Comprehensive Environmental Impact Assessment
                    </h3>
                    <div className="flex gap-2">
                      <button
                        onClick={() => window.print()}
                        className="text-sm bg-white/10 hover:bg-white/20 px-4 py-2 rounded-lg text-blue-200 transition-colors flex items-center gap-2"
                      >
                        🖨️ Print / Save PDF
                      </button>
                      <button
                        onClick={() => setResult({ ...result, detailed_report: null })}
                        className="text-sm bg-red-500/20 hover:bg-red-500/30 px-4 py-2 rounded-lg text-red-200 transition-colors"
                      >
                        ✕ Close Report
                      </button>
                    </div>
                  </div>
                  
                  {/* Report Header with Key Metrics */}
                  <div className="grid grid-cols-3 gap-4 mb-6 p-6 bg-gradient-to-r from-slate-800/50 to-slate-700/50 rounded-xl border border-white/10">
                    <div className="text-center">
                      <div className="text-sm text-slate-400 mb-1">Vessel MMSI</div>
                      <div className="text-xl font-mono font-bold text-cyan-400">{formData.mmsi}</div>
                    </div>
                    <div className="text-center">
                      <div className="text-sm text-slate-400 mb-1">CO₂ Emissions</div>
                      <div className="text-xl font-bold text-orange-400">
                        {result.estimated_co2_kg.toLocaleString(undefined, { maximumFractionDigits: 2 })} kg
                      </div>
                    </div>
                    <div className="text-center">
                      <div className="text-sm text-slate-400 mb-1">ESG Score</div>
                      <div className={`text-xl font-bold ${getScoreColor(result.esg_score)}`}>
                        {result.esg_score}/100 - {result.rating}
                      </div>
                    </div>
                  </div>
                  
                  {/* Operational Summary */}
                  <div className="mb-6 p-6 bg-white/5 rounded-xl">
                    <h4 className="text-lg font-bold text-white mb-4">Operational Summary</h4>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <span className="text-slate-400">Distance Traveled:</span>
                        <span className="text-white font-semibold ml-2">
                          {parseFloat(formData.total_distance_km).toFixed(2)} km
                        </span>
                      </div>
                      <div>
                        <span className="text-slate-400">Avg Speed:</span>
                        <span className="text-white font-semibold ml-2">
                          {parseFloat(formData.avg_speed).toFixed(1)} knots
                        </span>
                      </div>
                      <div>
                        <span className="text-slate-400">Time at Sea:</span>
                        <span className="text-white font-semibold ml-2">
                          {parseFloat(formData.time_at_sea_hours).toFixed(1)} hours
                        </span>
                      </div>
                      <div>
                        <span className="text-slate-400">Carbon Intensity:</span>
                        <span className="text-white font-semibold ml-2">
                          {(result.estimated_co2_kg / parseFloat(formData.total_distance_km)).toFixed(2)} kg/km
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  {/* Vessel Specifications */}
                  <div className="mb-6 p-6 bg-white/5 rounded-xl">
                    <h4 className="text-lg font-bold text-white mb-4">Vessel Specifications</h4>
                    <div className="grid grid-cols-3 gap-4 text-sm">
                      <div>
                        <span className="text-slate-400">Length:</span>
                        <span className="text-white font-semibold ml-2">{formData.length} m</span>
                      </div>
                      <div>
                        <span className="text-slate-400">Width:</span>
                        <span className="text-white font-semibold ml-2">{formData.width} m</span>
                      </div>
                      <div>
                        <span className="text-slate-400">Draft:</span>
                        <span className="text-white font-semibold ml-2">{formData.draft} m</span>
                      </div>
                    </div>
                  </div>
                  
                  {/* Weather Impact Section */}
                  {result.weather_impact !== undefined && (
                    <div className="mb-6 p-6 bg-gradient-to-r from-yellow-500/10 to-orange-500/10 rounded-xl border border-yellow-500/30">
                      <h4 className="text-lg font-bold text-white mb-4">Weather Impact Analysis</h4>
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                        <div>
                          <span className="text-slate-400">Base CO₂ Emissions:</span>
                          <span className="text-white font-semibold ml-2">
                            {result.estimated_co2_kg.toFixed(2)} kg
                          </span>
                        </div>
                        {result.weather_impact > 0 && (
                          <>
                            <div>
                              <span className="text-slate-400">Weather Impact:</span>
                              <span className="text-yellow-400 font-semibold ml-2">
                                +{result.weather_impact.toFixed(2)} kg CO₂
                              </span>
                            </div>
                            <div>
                              <span className="text-slate-400">Total with Weather:</span>
                              <span className="text-orange-400 font-semibold ml-2">
                                {(result.estimated_co2_kg + result.weather_impact).toFixed(2)} kg
                              </span>
                            </div>
                            {result.weather_conditions && (
                              <>
                                <div>
                                  <span className="text-slate-400">Wind Speed:</span>
                                  <span className="text-cyan-400 font-semibold ml-2">
                                    {result.weather_conditions.wind_speed_ms?.toFixed(1) || 'N/A'} m/s
                                  </span>
                                </div>
                                <div>
                                  <span className="text-slate-400">Wave Height:</span>
                                  <span className="text-cyan-400 font-semibold ml-2">
                                    {result.weather_conditions.wave_height_m?.toFixed(1) || 'N/A'} m
                                  </span>
                                </div>
                                <div>
                                  <span className="text-slate-400">Impact Percentage:</span>
                                  <span className="text-yellow-400 font-semibold ml-2">
                                    +{((result.weather_impact / result.estimated_co2_kg) * 100).toFixed(1)}%
                                  </span>
                                </div>
                              </>
                            )}
                          </>
                        )}
                        {result.weather_impact === 0 && (
                          <div className="col-span-2">
                            <span className="text-green-400 font-semibold">
                              ✓ Favorable weather conditions - No additional emissions
                            </span>
                          </div>
                        )}
                      </div>
                      {result.weather_impact > 0 && (
                        <div className="mt-4 p-3 bg-yellow-500/10 rounded border-l-4 border-yellow-500">
                          <p className="text-sm text-yellow-200">
                            <strong>Note:</strong> Weather conditions (wind, waves) have increased fuel consumption 
                            and emissions by {((result.weather_impact / result.estimated_co2_kg) * 100).toFixed(1)}%. 
                            Consider route optimization or voyage planning to minimize weather impact.
                          </p>
                        </div>
                      )}
                    </div>
                  )}
                  
                  {/* AI-Generated Report Content */}
                  <div className="prose prose-invert prose-lg max-w-none text-slate-300">
                    <MarkdownRenderer content={result.detailed_report} />
                  </div>
                  
                  {/* Report Footer */}
                  <div className="mt-8 pt-6 border-t border-white/10 text-sm text-slate-400 text-center">
                    <p>Report generated on {new Date().toLocaleString()}</p>
                    <p className="mt-1">ESG Scoring Pipeline - Maritime Environmental Analytics</p>
                  </div>
                </div>
              </div>
            ) : (
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
                  
                  {/* Generate Report Button */}
                  {!result.detailed_report && (
                    <div className="flex justify-center pt-8">
                      <button
                        onClick={handleGenerateReport}
                        disabled={loading}
                        className="flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-xl font-bold text-lg hover:from-emerald-400 hover:to-teal-400 disabled:opacity-50 transition-all shadow-xl hover:shadow-emerald-500/30 transform hover:-translate-y-1"
                      >
                        {loading ? (
                          <>
                            <svg className="animate-spin h-6 w-6" viewBox="0 0 24 24">
                              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                            </svg>
                            Generating Report...
                          </>
                        ) : (
                          '📄 Generate Detailed AI Report'
                        )}
                      </button>
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
            )}
          </>
          ) : (
            // Fleet Analysis View
            <FleetAnalysis />
          )}
        </main>
      </div>
    </div>
  );
}

export default AnalyzeVessel;
