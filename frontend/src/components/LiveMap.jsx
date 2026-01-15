
import React, { useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import AdvancedWeatherLayer from './AdvancedWeatherLayer';

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

// Wind indicator overlay component
const WindIndicatorLayer = ({ vessels, weatherOverlay }) => {
    const map = useMap();
    const windLayerRef = useRef(null);

    useEffect(() => {
        if (!map || weatherOverlay === 'none' || (!weatherOverlay.includes('wind') && !weatherOverlay.includes('full'))) {
            if (windLayerRef.current) {
                map.removeLayer(windLayerRef.current);
                windLayerRef.current = null;
            }
            return;
        }

        // Remove old layer
        if (windLayerRef.current) {
            map.removeLayer(windLayerRef.current);
        }

        // Create custom layer for wind arrows
        const svg = L.SVG.create('svg');
        windLayerRef.current = L.svgOverlay(svg, map.getBounds());

        vessels.forEach(vessel => {
            if (!vessel.weather || vessel.weather.wind_speed_ms === 0) return;

            const lat = vessel.latitude || vessel.lat;
            const lon = vessel.longitude || vessel.lon;
            const point = map.latLngToContainerPoint([lat, lon]);

            const angle = vessel.weather.wind_direction_deg;
            const speed = vessel.weather.wind_speed_ms;
            const arrowSize = Math.min(20 + speed * 2, 50);

            const radians = (angle * Math.PI) / 180;
            const tipX = Math.cos(radians) * (arrowSize / 2);
            const tipY = Math.sin(radians) * (arrowSize / 2);
            const baseX = -Math.cos(radians) * (arrowSize / 2);
            const baseY = -Math.sin(radians) * (arrowSize / 2);
            const leftX = baseX - Math.sin(radians) * 6;
            const leftY = baseY + Math.cos(radians) * 6;
            const rightX = baseX + Math.sin(radians) * 6;
            const rightY = baseY - Math.cos(radians) * 6;

            // Create line for wind shaft
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', point.x + baseX);
            line.setAttribute('y1', point.y + baseY);
            line.setAttribute('x2', point.x + tipX);
            line.setAttribute('y2', point.y + tipY);
            line.setAttribute('stroke', '#00d4ff');
            line.setAttribute('stroke-width', '2.5');
            line.setAttribute('opacity', '0.8');
            svg.appendChild(line);

            // Create arrow head
            const polygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
            polygon.setAttribute(
                'points',
                `${point.x + tipX},${point.y + tipY} ${point.x + leftX},${point.y + leftY} ${point.x + rightX},${point.y + rightY}`
            );
            polygon.setAttribute('fill', '#00d4ff');
            polygon.setAttribute('opacity', '0.9');
            svg.appendChild(polygon);

            // Add speed label
            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', point.x);
            text.setAttribute('y', point.y + arrowSize / 2 + 18);
            text.setAttribute('font-size', '11');
            text.setAttribute('text-anchor', 'middle');
            text.setAttribute('fill', '#00d4ff');
            text.setAttribute('font-weight', 'bold');
            text.setAttribute('opacity', '0.9');
            text.textContent = `${speed.toFixed(0)}m/s`;
            svg.appendChild(text);
        });

        map.addLayer(windLayerRef.current);

        return () => {
            if (windLayerRef.current) {
                map.removeLayer(windLayerRef.current);
            }
        };
    }, [map, vessels, weatherOverlay]);

    return null;
};

// Precipitation color overlay component
const PrecipitationColorLayer = ({ vessels, weatherOverlay }) => {
    const map = useMap();
    const precipLayerRef = useRef(null);

    const getPrecipitationColor = (condition, waveHeight) => {
        const conditionLower = (condition || '').toLowerCase();

        if (waveHeight > 3) return '#dc2626';       // Red - heavy
        if (waveHeight > 2) return '#f97316';       // Orange
        if (waveHeight > 1) return '#fbbf24';       // Amber
        if (waveHeight > 0.5) return '#06b6d4';    // Cyan - light

        if (conditionLower.includes('thunderstorm') || conditionLower.includes('storm'))
            return '#991b1b';
        if (conditionLower.includes('rain') || conditionLower.includes('drizzle'))
            return '#f97316';
        if (conditionLower.includes('snow'))
            return '#e0e7ff';
        if (conditionLower.includes('cloud'))
            return '#60a5fa';
        if (conditionLower.includes('mist') || conditionLower.includes('fog'))
            return '#9ca3af';

        return '#4ade80'; // Green - clear
    };

    useEffect(() => {
        if (!map || weatherOverlay === 'none' || (!weatherOverlay.includes('precipitation') && !weatherOverlay.includes('full'))) {
            if (precipLayerRef.current) {
                map.removeLayer(precipLayerRef.current);
                precipLayerRef.current = null;
            }
            return;
        }

        if (precipLayerRef.current) {
            map.removeLayer(precipLayerRef.current);
        }

        // Create feature group for precipitation circles
        const featureGroup = L.featureGroup();

        vessels.forEach(vessel => {
            if (!vessel.weather) return;

            const lat = vessel.latitude || vessel.lat;
            const lon = vessel.longitude || vessel.lon;
            const color = getPrecipitationColor(vessel.weather.condition, vessel.weather.wave_height_m);

            const circle = L.circleMarker([lat, lon], {
                radius: 18,
                fillColor: color,
                color: color,
                weight: 2,
                opacity: 0.5,
                fillOpacity: 0.25
            });

            circle.bindPopup(
                `<div class="text-xs text-white">
                    <div class="font-semibold text-cyan-300 mb-1">Precipitation</div>
                    <p><span class="font-semibold">Condition:</span> ${vessel.weather.condition}</p>
                    <p><span class="font-semibold">Wave Height:</span> ${vessel.weather.wave_height_m?.toFixed(1)} m</p>
                </div>`
            );

            featureGroup.addLayer(circle);
        });

        precipLayerRef.current = featureGroup;
        map.addLayer(featureGroup);

        return () => {
            if (precipLayerRef.current) {
                map.removeLayer(precipLayerRef.current);
            }
        };
    }, [map, vessels, weatherOverlay]);

    return null;
};

const LiveMap = ({ vessels, center = [1.290270, 103.851959], zoom = 10, weatherOverlay = 'none' }) => {
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

                {/* Weather overlay layers */}
                <AdvancedWeatherLayer vessels={vessels} overlayType={weatherOverlay} />
                <PrecipitationColorLayer vessels={vessels} weatherOverlay={weatherOverlay} />
                <WindIndicatorLayer vessels={vessels} weatherOverlay={weatherOverlay} />

                {vessels.map((vessel) => (
                    <Marker
                        key={vessel.mmsi}
                        position={[vessel.latitude || vessel.lat, vessel.longitude || vessel.lon]}
                        icon={createBadgeIcon(vessel.esg_color === 'green' ? '#4ade80' : vessel.esg_color === 'red' ? '#ef4444' : vessel.esg_color === 'orange' ? '#f97316' : '#eab308')}
                    >
                        <Popup className="glass-popup">
                            <div className="p-3 min-w-[280px] bg-slate-950 text-white rounded text-xs">
                                {/* Vessel Info */}
                                <h3 className="font-bold text-cyan-300 text-sm">{vessel.vessel_name}</h3>
                                <div className="text-slate-400 mt-2 space-y-1">
                                    <p><span className="font-semibold">MMSI:</span> {vessel.mmsi}</p>
                                    <p><span className="font-semibold">Speed:</span> {(vessel.speed_knots || vessel.speed || 0).toFixed(1)} kts</p>
                                    <p><span className="font-semibold">ESG Score:</span> <span className={`font-bold ${vessel.esg_score >= 90 ? 'text-green-400' :
                                        vessel.esg_score >= 70 ? 'text-blue-400' :
                                            vessel.esg_score >= 50 ? 'text-yellow-400' : 'text-red-400'
                                        }`}>{vessel.esg_score}</span> ({vessel.rating || 'Unknown'})</p>
                                </div>

                                {/* Weather Section */}
                                {vessel.weather && (
                                    <div className="mt-3 pt-3 border-t border-slate-700">
                                        <h4 className="font-semibold text-cyan-300 mb-1">Weather Conditions</h4>
                                        <div className="text-slate-400 space-y-0.5">
                                            <p><span className="font-semibold">Wind:</span> {vessel.weather.wind_speed_ms?.toFixed(1) || 'N/A'} m/s @ {vessel.weather.wind_direction_deg || 'N/A'}°</p>
                                            <p><span className="font-semibold">Waves:</span> {vessel.weather.wave_height_m?.toFixed(1) || 'N/A'} m</p>
                                            <p><span className="font-semibold">Condition:</span> {vessel.weather.condition || 'Clear'}</p>
                                            <p><span className="font-semibold">Resistance Factor:</span> <span className={`font-bold ${vessel.weather.weather_resistance_factor > 1.2 ? 'text-orange-400' : 'text-green-400'}`}>×{vessel.weather.weather_resistance_factor?.toFixed(2) || '1.00'}</span></p>
                                            {(vessel.weather.storm_flag || vessel.weather.rough_sea_flag) && (
                                                <p className="text-red-400 font-semibold">
                                                    ⚠️ {vessel.weather.storm_flag ? 'Storm' : ''} {vessel.weather.rough_sea_flag ? 'Rough Seas' : ''}
                                                </p>
                                            )}
                                        </div>
                                    </div>
                                )}

                                {/* Emissions Section */}
                                {vessel.base_co2 && (
                                    <div className="mt-3 pt-3 border-t border-slate-700">
                                        <h4 className="font-semibold text-cyan-300 mb-1">CO₂ Emissions</h4>
                                        <div className="text-slate-400 space-y-0.5">
                                            <p><span className="font-semibold">Baseline:</span> <span className="text-blue-400">{vessel.base_co2?.toFixed(0) || 'N/A'}</span> kg</p>
                                            <p><span className="font-semibold">Adjusted:</span> <span className={`font-bold ${vessel.adjusted_co2 > vessel.base_co2 ? 'text-orange-400' : 'text-green-400'}`}>{vessel.adjusted_co2?.toFixed(0) || 'N/A'}</span> kg</p>
                                            {vessel.delta_weather && (
                                                <p><span className="font-semibold">Weather Impact:</span> <span className="text-yellow-400">+{vessel.delta_weather?.toFixed(0)}</span> kg ({((vessel.delta_weather / vessel.base_co2) * 100)?.toFixed(1)}%)</p>
                                            )}
                                        </div>
                                    </div>
                                )}

                                {/* Risk Flags */}
                                {vessel.risk_flags && vessel.risk_flags.length > 0 && (
                                    <div className="mt-3 pt-3 border-t border-slate-700">
                                        <div className="bg-red-500/20 border border-red-500/40 text-red-300 p-2 rounded text-xs">
                                            <span className="font-semibold">🚩 Risks:</span> {vessel.risk_flags.join(', ')}
                                        </div>
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
