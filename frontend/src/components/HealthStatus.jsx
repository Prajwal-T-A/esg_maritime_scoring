/**
 * Health Status Component
 * Displays backend API health check status
 * 
 * Shows a visual indicator (green/red) to show if backend is running
 */

import React, { useEffect, useState } from 'react';
import apiService from '../services/api';

function HealthStatus() {
  // State to track backend health
  const [health, setHealth] = useState({
    status: 'checking',
    message: 'Checking backend...',
  });

  /**
   * Check backend health when component mounts
   * useEffect runs once when component loads
   */
  useEffect(() => {
    checkBackendHealth();
  }, []);

  /**
   * Function to check backend health
   * Calls API service and updates state
   */
  const checkBackendHealth = async () => {
    const result = await apiService.checkHealth();
    
    if (result.success) {
      setHealth({
        status: 'ok',
        message: 'Backend connected',
        timestamp: result.data.timestamp,
      });
    } else {
      setHealth({
        status: 'error',
        message: result.error,
      });
    }
  };

  /**
   * Determine indicator color based on status
   */
  const getIndicatorColor = () => {
    if (health.status === 'ok') return 'bg-green-500';
    if (health.status === 'error') return 'bg-red-500';
    return 'bg-yellow-500';
  };

  return (
    <div className="flex items-center gap-2 text-sm">
      {/* Status indicator dot */}
      <div className={`w-3 h-3 rounded-full ${getIndicatorColor()} animate-pulse`}></div>
      
      {/* Status text */}
      <span className="text-gray-700">
        {health.message}
      </span>

      {/* Refresh button */}
      <button
        onClick={checkBackendHealth}
        className="ml-2 text-blue-600 hover:text-blue-800 underline text-xs"
      >
        Refresh
      </button>
    </div>
  );
}

export default HealthStatus;
