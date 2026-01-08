/**
 * ESG Score Card Component
 * Displays ESG environmental score with color coding
 * 
 * Color scheme:
 * - Green (>= 80): Excellent environmental performance
 * - Orange (60-79): Moderate environmental performance
 * - Red (< 60): Poor environmental performance
 */

import React from 'react';

function ESGScoreCard({ score, co2Emissions, timestamp }) {
  /**
   * Determine score category and color
   * Returns object with color, label, and CSS classes
   */
  const getScoreCategory = () => {
    if (score >= 80) {
      return {
        color: 'esg-green',
        bgColor: 'bg-green-100',
        borderColor: 'border-green-500',
        textColor: 'text-green-800',
        label: 'Excellent',
      };
    } else if (score >= 60) {
      return {
        color: 'esg-orange',
        bgColor: 'bg-orange-100',
        borderColor: 'border-orange-500',
        textColor: 'text-orange-800',
        label: 'Moderate',
      };
    } else {
      return {
        color: 'esg-red',
        bgColor: 'bg-red-100',
        borderColor: 'border-red-500',
        textColor: 'text-red-800',
        label: 'Needs Improvement',
      };
    }
  };

  const category = getScoreCategory();

  return (
    <div className={`p-6 rounded-lg border-2 ${category.borderColor} ${category.bgColor}`}>
      {/* Header */}
      <div className="text-center mb-4">
        <h3 className="text-lg font-semibold text-gray-700">ESG Environmental Score</h3>
      </div>

      {/* Score Display */}
      <div className="text-center mb-4">
        <div className={`text-6xl font-bold ${category.textColor}`}>
          {score}
        </div>
        <div className={`text-xl font-semibold ${category.textColor} mt-2`}>
          {category.label}
        </div>
      </div>

      {/* CO2 Emissions */}
      {co2Emissions !== undefined && (
        <div className="mt-4 pt-4 border-t border-gray-300">
          <div className="text-center">
            <p className="text-sm text-gray-600">Estimated CO₂ Emissions</p>
            <p className="text-2xl font-semibold text-gray-800">
              {co2Emissions.toFixed(2)} kg
            </p>
          </div>
        </div>
      )}

      {/* Timestamp */}
      {timestamp && (
        <div className="mt-3 text-center">
          <p className="text-xs text-gray-500">
            Last Updated: {new Date(timestamp).toLocaleString()}
          </p>
        </div>
      )}

      {/* Score Guide */}
      <div className="mt-6 pt-4 border-t border-gray-300">
        <p className="text-xs text-gray-600 text-center mb-2">Score Guide:</p>
        <div className="flex justify-around text-xs">
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 bg-green-500 rounded"></div>
            <span className="text-gray-600">80-100</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 bg-orange-500 rounded"></div>
            <span className="text-gray-600">60-79</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 bg-red-500 rounded"></div>
            <span className="text-gray-600">&lt; 60</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ESGScoreCard;
