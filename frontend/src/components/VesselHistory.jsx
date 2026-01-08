/**
 * Vessel History Component
 * Displays historical AIS records in a table format
 * 
 * Shows time-series data for a vessel with all metrics
 */

import React from 'react';

function VesselHistory({ data, loading }) {
  /**
   * Format timestamp to readable format
   */
  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  /**
   * Get color for ESG score
   */
  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600 font-semibold';
    if (score >= 60) return 'text-orange-600 font-semibold';
    return 'text-red-600 font-semibold';
  };

  // Loading state
  if (loading) {
    return (
      <div className="bg-white p-8 rounded-lg border border-gray-200 shadow-sm">
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="ml-4 text-gray-600">Loading history...</p>
        </div>
      </div>
    );
  }

  // No data state
  if (!data || data.length === 0) {
    return (
      <div className="bg-gray-50 p-8 rounded-lg border border-gray-200">
        <p className="text-gray-500 text-center">No historical data available</p>
        <p className="text-gray-400 text-center text-sm mt-2">
          Enter a valid MMSI to view vessel history
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
      {/* Header */}
      <div className="bg-gray-50 px-6 py-4 border-b border-gray-200">
        <h3 className="text-xl font-semibold text-gray-800">Vessel History</h3>
        <p className="text-sm text-gray-500 mt-1">
          {data.length} record{data.length !== 1 ? 's' : ''} found
        </p>
      </div>

      {/* Table - Scrollable on small screens */}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          {/* Table Header */}
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Timestamp
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Location
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Speed
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                CO₂ (kg)
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                ESG Score
              </th>
            </tr>
          </thead>

          {/* Table Body */}
          <tbody className="bg-white divide-y divide-gray-200">
            {data.map((record, index) => (
              <tr key={index} className="hover:bg-gray-50 transition-colors">
                {/* Timestamp */}
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {formatTimestamp(record.timestamp)}
                </td>

                {/* Location */}
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  <div className="font-mono text-xs">
                    {record.latitude.toFixed(2)}°, {record.longitude.toFixed(2)}°
                  </div>
                </td>

                {/* Speed */}
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {record.speed_knots.toFixed(1)} kn
                </td>

                {/* CO2 */}
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {record.estimated_co2_kg.toFixed(2)}
                </td>

                {/* ESG Score */}
                <td className={`px-6 py-4 whitespace-nowrap text-sm ${getScoreColor(record.esg_environment_score)}`}>
                  {record.esg_environment_score}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Footer Summary */}
      <div className="bg-gray-50 px-6 py-3 border-t border-gray-200">
        <div className="flex justify-between text-sm text-gray-600">
          <span>
            Average CO₂: {(data.reduce((sum, r) => sum + r.estimated_co2_kg, 0) / data.length).toFixed(2)} kg
          </span>
          <span>
            Average ESG: {Math.round(data.reduce((sum, r) => sum + r.esg_environment_score, 0) / data.length)}
          </span>
        </div>
      </div>
    </div>
  );
}

export default VesselHistory;
