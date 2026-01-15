
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
                            <div className="p-2 min-w-[200px]">
                                <h3 className="font-bold text-gray-800">{vessel.vessel_name}</h3>
                                <div className="text-sm text-gray-600 mt-1">
                                    <p>MMSI: {vessel.mmsi}</p>
                                    <p>Speed: {vessel.speed.toFixed(1)} kts</p>
                                    <p>ESG Score: <span className={`font-bold ${vessel.esg_score >= 90 ? 'text-green-600' :
                                        vessel.esg_score >= 70 ? 'text-blue-600' :
                                            vessel.esg_score >= 50 ? 'text-yellow-600' : 'text-red-600'
                                        }`}>{vessel.esg_score}</span></p>
                                </div>
                                {vessel.risk_flags && vessel.risk_flags.length > 0 && (
                                    <div className="mt-2 text-xs bg-red-50 text-red-700 p-1 rounded">
                                        {vessel.risk_flags.join(', ')}
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
