
import React from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix for default marker icons in React-Leaflet
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

// Custom icons for ESG scores
const createBadgeIcon = (color) => {
    return L.divIcon({
        className: 'custom-icon',
        html: `<div style="
      background-color: ${color};
      width: 12px;
      height: 12px;
      border-radius: 50%;
      border: 2px solid white;
      box-shadow: 0 0 4px rgba(0,0,0,0.4);
    "></div>`,
        iconSize: [12, 12],
        iconAnchor: [6, 6]
    });
};

const LiveMap = ({ vessels, center = [1.290270, 103.851959], zoom = 10 }) => {
    // Generate a unique key based on the center coordinates to force remount only when sector changes
    const mapKey = `${center[0]}-${center[1]}`;

    return (
        <div className="h-full w-full rounded-xl overflow-hidden shadow-lg border border-white/20">
            <MapContainer
                key={mapKey}
                center={center}
                zoom={zoom}
                style={{ height: '100%', width: '100%' }}
                className="z-0"
            >
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                />

                {vessels.map((vessel) => (
                    <Marker
                        key={vessel.mmsi}
                        position={[vessel.lat, vessel.lon]}
                        icon={createBadgeIcon(vessel.esg_color === 'green' ? '#4ade80' : vessel.esg_color === 'red' ? '#ef4444' : vessel.esg_color === 'orange' ? '#f97316' : '#eab308')}
                    >
                        <Popup className="glass-popup">
                            <div className="p-2 min-w-[250px]">
                                <h3 className="font-bold text-gray-800 mb-2">{vessel.vessel_name}</h3>
                                <div className="text-sm text-gray-600 space-y-1">
                                    <p><span className="font-semibold">MMSI:</span> {vessel.mmsi}</p>
                                    <p><span className="font-semibold">Speed:</span> {vessel.speed.toFixed(1)} kts</p>
                                    <p><span className="font-semibold">ESG Score:</span> <span className={`font-bold ${vessel.esg_score >= 90 ? 'text-green-600' :
                                        vessel.esg_score >= 70 ? 'text-blue-600' :
                                            vessel.esg_score >= 50 ? 'text-yellow-600' : 'text-red-600'
                                        }`}>{vessel.esg_score}</span></p>
                                    
                                    {vessel.weather && vessel.weather.wind_speed_ms !== undefined && (
                                        <div className="mt-2 pt-2 border-t border-gray-300">
                                            <p className="font-semibold text-gray-700 mb-1">Weather Conditions:</p>
                                            <p className="text-xs">💨 Wind: {vessel.weather.wind_speed_ms.toFixed(1)} m/s</p>
                                            <p className="text-xs">🌊 Waves: {vessel.weather.wave_height_m.toFixed(1)} m</p>
                                            <p className="text-xs">🌡️ Temp: {vessel.weather.temperature_c?.toFixed(1) || 'N/A'}°C</p>
                                            <p className="text-xs">☁️ {vessel.weather.weather_condition || 'N/A'}</p>
                                            {vessel.delta_weather !== undefined && vessel.delta_weather > 0 && (
                                                <p className="text-xs font-semibold text-orange-600 mt-1">
                                                    +{vessel.delta_weather.toFixed(0)} kg CO₂ (weather impact)
                                                </p>
                                            )}
                                        </div>
                                    )}
                                </div>
                                {vessel.risk_flags && vessel.risk_flags.length > 0 && (
                                    <div className="mt-2 text-xs bg-red-50 text-red-700 p-1 rounded">
                                        ⚠️ {vessel.risk_flags.join(', ')}
                                    </div>
                                )}
                            </div>
                        </Popup>
                    </Marker>
                ))}
            </MapContainer>
        </div>
    );
};

export default LiveMap;
