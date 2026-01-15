/**
 * TypeScript interfaces for Live Vessel Tracking with Weather Enrichment
 */

export interface WeatherData {
  wind_speed_ms: number;
  wind_direction_deg: number;
  weather_condition: string;
  weather_description: string;
  wave_height_m: number;
  weather_resistance_factor: number;
  storm_flag: boolean;
  rough_sea_flag: boolean;
  temperature_c: number;
  humidity_percent: number;
}

export interface EmissionData {
  base_co2_kg: number;
  adjusted_co2_kg: number;
  delta_due_to_weather: number;
  resistance_factor: number;
  weather_impact_percent: number;
}

export interface VesselUpdate {
  mmsi: string;
  lat: number;
  lon: number;
  speed: number;
  heading: number;
  timestamp: string;
  esg_score: number;
  rating: string;
  esg_color: string;
  vessel_name: string;
  sector: string;
  risk_flags: string[];
  weather: WeatherData;
  base_co2: number;
  adjusted_co2: number;
  delta_weather: number;
}

export type WeatherOverlayMode = 'none' | 'precipitation' | 'wind' | 'temperature' | 'full';

export interface LiveTrackingState {
  vessels: Record<string, VesselUpdate>;
  connectionStatus: string;
  selectedSector: string;
  weatherOverlay: WeatherOverlayMode;
}
