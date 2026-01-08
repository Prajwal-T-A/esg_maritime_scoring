/**
 * API Service Layer
 * Centralized API calls to FastAPI backend
 * 
 * This file contains all HTTP requests to the backend.
 * Makes it easy to modify API logic in one place.
 */

import axios from 'axios';

// Get backend URL from environment variable (.env file)
// Defaults to localhost:8000 if not set
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://127.0.0.1:8000';
const API_PREFIX = '/api/v1';

/**
 * Create axios instance with base configuration
 * This ensures all requests use the same base URL
 */
const apiClient = axios.create({
  baseURL: `${API_BASE_URL}${API_PREFIX}`,
  timeout: 10000, // 10 second timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * API Service Object
 * Contains all API call functions
 */
const apiService = {
  /**
   * Check backend health status
   * @returns {Promise} Response with status and timestamp
   */
  checkHealth: async () => {
    try {
      const response = await apiClient.get('/health');
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || error.message || 'Backend is not responding',
      };
    }
  },

  /**
   * Fetch latest AIS record for a vessel
   * @param {string} mmsi - Maritime Mobile Service Identity
   * @returns {Promise} Latest vessel data
   */
  getVesselLatest: async (mmsi) => {
    try {
      const response = await apiClient.get(`/vessels/${mmsi}/latest`);
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || `Failed to fetch data for MMSI: ${mmsi}`,
      };
    }
  },

  /**
   * Fetch historical AIS records for a vessel
   * @param {string} mmsi - Maritime Mobile Service Identity
   * @returns {Promise} Array of historical records
   */
  getVesselHistory: async (mmsi) => {
    try {
      const response = await apiClient.get(`/vessels/${mmsi}/history`);
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || `Failed to fetch history for MMSI: ${mmsi}`,
      };
    }
  },

  /**
   * Fetch ESG metrics for a vessel
   * @param {string} mmsi - Maritime Mobile Service Identity
   * @returns {Promise} ESG data (CO2, score, timestamp)
   */
  getESGMetrics: async (mmsi) => {
    try {
      const response = await apiClient.get(`/esg/${mmsi}`);
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || `Failed to fetch ESG data for MMSI: ${mmsi}`,
      };
    }
  },
};

export default apiService;
