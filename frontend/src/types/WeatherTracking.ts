/**
 * Weather-Enriched Live Tracking WebSocket Payload Interface
 * 
 * TypeScript interfaces for real-time vessel tracking with weather integration
 * and ML-based emissions analysis.
 */

/**
 * Real-time weather data for a location
 */
export interface WeatherData {
  /** Wind speed in meters per second */
  wind_speed_ms: number;
  
  /** Wind direction in degrees (0-360) */
  wind_direction_deg: number;
  
  /** Weather condition description */
  condition: 'clear' | 'rain' | 'storm' | 'clouds' | string;
  
  /** Wave height in meters (may be null if unavailable) */
  wave_height_m?: number | null;
  
  /** ISO 8601 timestamp of weather observation */
  timestamp: string;
  
  /** Weather resistance multiplier (≥1.0) */
  weather_resistance_factor: number;
  
  /** True if storm conditions (thunderstorm, tornado) detected */
  storm_flag: boolean;
  
  /** True if wave height > 3 meters */
  rough_sea_flag: boolean;
}

/**
 * Weather-adjusted emissions data
 */
export interface WeatherAdjustedEmissions {
  /** Baseline CO2 emissions without weather adjustment (kg) */
  base_co2_kg: number;
  
  /** Weather-adjusted CO2 emissions (kg) */
  adjusted_co2_kg: number;
  
  /** Delta in emissions due to weather impact (kg) */
  delta_due_to_weather: number;
  
  /** Speed adjusted by weather resistance factor (knots) */
  adjusted_speed_knots: number;
  
  /** Applied weather resistance multiplier */
  weather_resistance_factor: number;
}

/**
 * Live tracking WebSocket payload with weather enrichment
 * 
 * Streamed to frontend every 2 seconds with real-time vessel data,
 * weather conditions, and ML-based ESG scoring.
 */
export interface LiveTrackingPayload {
  /** Maritime Mobile Service Identity (vessel identifier) */
  mmsi: string;
  
  /** Current latitude coordinate */
  latitude: number;
  
  /** Current longitude coordinate */
  longitude: number;
  
  /** Current speed in knots */
  speed_knots: number;
  
  /** ISO 8601 timestamp */
  timestamp: string;
  
  /** Real-time weather information */
  weather: WeatherData;
  
  /** Baseline CO2 emissions without weather adjustment (kg) */
  base_co2: number;
  
  /** Weather-adjusted CO2 emissions (kg) */
  adjusted_co2: number;
  
  /** Delta in emissions due to weather (kg) */
  delta_weather: number;
  
  /** Environmental ESG score (0-100, higher is better) */
  esg_score: number;
  
  /** ESG rating (Excellent/Good/Moderate/Poor/Critical) */
  rating: 'Excellent' | 'Good' | 'Moderate' | 'Poor' | 'Critical';
  
  /** Color for UI visualization */
  esg_color: 'green' | 'blue' | 'yellow' | 'orange' | 'red';
  
  /** Environmental and weather-related risk indicators */
  risk_flags: string[];
  
  /** Vessel name/display identifier */
  vessel_name?: string;
  
  /** Operational sector/region */
  sector?: string;
  
  /** Whether data is from simulation (true) or live AIS (false) */
  is_simulation?: boolean;
}

/**
 * Risk flag types that can appear in live tracking
 */
export type RiskFlagType =
  | 'High CO2 intensity'
  | 'Excessive acceleration'
  | 'Excessive speed'
  | 'Long continuous operation'
  | 'Storm navigation'
  | 'High wave resistance'
  | 'Strong wind conditions'
  | 'Model Unavailable'
  | string;

/**
 * WebSocket connection state
 */
export interface WebSocketState {
  /** Whether connection is open */
  connected: boolean;
  
  /** Last message received timestamp */
  lastMessageTime?: number;
  
  /** Connection error (if any) */
  error?: string;
  
  /** Number of reconnection attempts */
  reconnectAttempts: number;
}

/**
 * Vessel tracking update from WebSocket
 */
export interface VesselUpdate extends LiveTrackingPayload {
  // Extends LiveTrackingPayload with all required fields
}

/**
 * Aggregated vessel statistics for dashboard
 */
export interface VesselStatistics {
  /** Total vessels tracked */
  totalVessels: number;
  
  /** Vessels with excellent ESG score (≥90) */
  excellentCount: number;
  
  /** Vessels with good ESG score (70-89) */
  goodCount: number;
  
  /** Vessels with moderate ESG score (50-69) */
  moderateCount: number;
  
  /** Vessels with poor ESG score (30-49) */
  poorCount: number;
  
  /** Vessels with critical ESG score (<30) */
  criticalCount: number;
  
  /** Average weather resistance factor across all vessels */
  avgWeatherResistance: number;
  
  /** Number of vessels in storm conditions */
  vesselInStorm: number;
  
  /** Average CO2 delta due to weather */
  avgWeatherDelta: number;
}

/**
 * Map viewport for GIS display
 */
export interface MapViewport {
  /** Center latitude */
  latitude: number;
  
  /** Center longitude */
  longitude: number;
  
  /** Zoom level */
  zoom: number;
}

/**
 * Sector configuration
 */
export interface SectorConfig {
  /** Sector name (e.g., "Singapore", "Mumbai") */
  name: string;
  
  /** Bounding box [[lon_min, lat_min], [lon_max, lat_max]] */
  bounds: [[number, number], [number, number]];
  
  /** Color for visualization */
  color?: string;
}

/**
 * Historical ESG trend data point
 */
export interface ESGTrendPoint {
  /** ISO 8601 timestamp */
  timestamp: string;
  
  /** ESG score at this time */
  score: number;
  
  /** Base CO2 at this time */
  base_co2: number;
  
  /** Weather-adjusted CO2 at this time */
  adjusted_co2: number;
  
  /** Weather resistance factor at this time */
  weather_factor: number;
}

/**
 * Complete vessel profile
 */
export interface VesselProfile {
  /** Maritime Mobile Service Identity */
  mmsi: string;
  
  /** Vessel name */
  name: string;
  
  /** Current location */
  location: {
    latitude: number;
    longitude: number;
    timestamp: string;
  };
  
  /** Current ESG metrics */
  currentESG: {
    score: number;
    rating: string;
    riskFlags: string[];
  };
  
  /** Current emissions */
  currentEmissions: {
    base_co2: number;
    adjusted_co2: number;
    weatherDelta: number;
  };
  
  /** Current weather */
  currentWeather: WeatherData;
  
  /** ESG trend over time */
  esgTrend?: ESGTrendPoint[];
}
