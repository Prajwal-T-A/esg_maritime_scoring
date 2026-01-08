/**
 * Vessel Latest Data Component
 * Displays the most recent AIS record for a vessel
 * 
 * Shows all vessel information including location, speed, and ESG data
 */

import React from 'react';

function VesselLatest({ data }) {
  // If no data, show message
  if (!data) {
    return (
      <div className="bg-gray-50 p-6 rounded-lg border border-gray-200">
        <p className="text-gray-500 text-center">No vessel data available</p>
      </div>
    );
  }

  /**
   * Format timestamp to readable date/time
   */
  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  return (
    <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
      {/* Header */}
      <div className="mb-4 pb-3 border-b border-gray-200">
        <h3 className="text-xl font-semibold text-gray-800">Latest Vessel Data</h3>
        <p className="text-sm text-gray-500 mt-1">
          Most recent AIS record for MMSI: <span className="font-mono font-semibold">{data.mmsi}</span>
        </p>
      </div>

      {/* Data Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Location Information */}
        <div className="space-y-3">
          <h4 className="font-semibold text-gray-700 text-sm uppercase tracking-wide">
            Location
          </h4>
          
          <div className="bg-blue-50 p-3 rounded border border-blue-200">
            <p className="text-sm text-gray-600">Latitude</p>
            <p className="text-lg font-semibold text-gray-800">{data.latitude.toFixed(4)}°</p>
          </div>

          <div className="bg-blue-50 p-3 rounded border border-blue-200">
            <p className="text-sm text-gray-600">Longitude</p>
            <p className="text-lg font-semibold text-gray-800">{data.longitude.toFixed(4)}°</p>
          </div>

          <div className="bg-blue-50 p-3 rounded border border-blue-200">
            <p className="text-sm text-gray-600">Speed</p>
            <p className="text-lg font-semibold text-gray-800">{data.speed_knots.toFixed(1)} knots</p>
          </div>
        </div>

        {/* ESG & Emissions */}
        <div className="space-y-3">
          <h4 className="font-semibold text-gray-700 text-sm uppercase tracking-wide">
            Environmental Metrics
          </h4>

          <div className="bg-green-50 p-3 rounded border border-green-200">
            <p className="text-sm text-gray-600">ESG Score</p>
            <p className="text-lg font-semibold text-gray-800">{data.esg_environment_score}/100</p>
          </div>

          <div className="bg-orange-50 p-3 rounded border border-orange-200">
            <p className="text-sm text-gray-600">Estimated CO₂ Emissions</p>
            <p className="text-lg font-semibold text-gray-800">{data.estimated_co2_kg.toFixed(2)} kg</p>
          </div>

          <div className="bg-gray-50 p-3 rounded border border-gray-200">
            <p className="text-sm text-gray-600">Timestamp</p>
            <p className="text-sm font-medium text-gray-800">{formatTimestamp(data.timestamp)}</p>
          </div>
        </div>
      </div>

      {/* Additional Info */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <p className="text-xs text-gray-500 text-center">
          Data retrieved from S3 via FastAPI backend
        </p>
      </div>
    </div>
  );
}

export default VesselLatest;
