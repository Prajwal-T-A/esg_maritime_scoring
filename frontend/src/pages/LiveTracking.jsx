
import React, { useEffect, useState, useRef } from 'react';
import LiveMap from '../components/LiveMap';

const sectors = {
    Singapore: { center: [1.290270, 103.851959], zoom: 10 },
    India: { center: [18.9667, 72.8333], zoom: 9 }, // Mumbai center
    Visakhapatnam: { center: [17.7, 83.3], zoom: 11 }, // Visakhapatnam Port
    Mangalore: { center: [12.9, 74.8], zoom: 11 } // New Mangalore Port
};

const LiveTracking = () => {
    const [vessels, setVessels] = useState({});
    const [connectionStatus, setConnectionStatus] = useState('Connecting...');
    const [selectedSector, setSelectedSector] = useState('Singapore');
    const [weatherOverlay, setWeatherOverlay] = useState('none'); // 'none', 'precipitation', 'wind', 'full'

    // Use a map to store vessels by MMSI to avoid duplicates and easy updates
    const vesselsRef = useRef({});

    useEffect(() => {
        // Determine WebSocket protocol based on current window protocol
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//localhost:8000/api/v1/ws/live-vessels`;

        let ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            setConnectionStatus('Connected (Live Stream)');
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                // data is a single vessel update
                vesselsRef.current = {
                    ...vesselsRef.current,
                    [data.mmsi]: data
                };

                // Batch updates to state to render smoother (update every message is fine for low traffic)
                // For existing simulation, we get bursts.
                setVessels({ ...vesselsRef.current });

            } catch (e) {
                console.error("Error parsing WS message", e);
            }
        };

        ws.onerror = (error) => {
            console.error("WebSocket error:", error);
            setConnectionStatus('Connection Error - Retrying...');
        };

        ws.onclose = () => {
            setConnectionStatus('Disconnected');
            // Simple reconnect logic could go here
        };

        return () => {
            if (ws) ws.close();
        };
    }, []);

    const vesselList = Object.values(vessels);

    return (
        <div className="min-h-screen bg-slate-900 text-white relative overflow-hidden">
            {/* Background Overlay */}
            <div className="absolute inset-0 z-0 opacity-20 bg-[url('https://images.unsplash.com/photo-1516961642265-531546e84af2?q=80&w=2070&auto=format&fit=crop')] bg-cover bg-center"></div>

            <div className="relative z-10 container mx-auto px-4 py-8 h-screen flex flex-col">
                <header className="mb-6 flex justify-between items-center bg-white/5 p-4 rounded-xl border border-white/10 backdrop-blur-md">
                    <div>
                        <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
                            Live Vessel Tracking
                        </h1>
                        <div className="flex items-center gap-2 mt-1">
                            <select
                                value={selectedSector}
                                onChange={(e) => setSelectedSector(e.target.value)}
                                className="bg-slate-800 border border-white/20 text-xs rounded px-2 py-1 text-slate-300 focus:outline-none focus:border-cyan-500"
                            >
                                <option value="Singapore">Sector: Singapore Strait</option>
                                <option value="India">Sector: Indian Coast (Mumbai)</option>
                                <option value="Visakhapatnam">Sector: Visakhapatnam Port</option>
                                <option value="Mangalore">Sector: Mangalore Port</option>
                            </select>
                            <p className="text-slate-400 text-xs text-slate-500">
                                • Real-time ESG monitoring
                            </p>
                        </div>
                    </div>
                    <div className="flex items-center gap-4">
                        {/* Weather Overlay Toggle */}
                        <div className="flex items-center gap-2 bg-slate-800/50 rounded-lg px-3 py-1.5 border border-white/10">
                            <label className="text-xs text-slate-400 font-semibold">⛅ Weather:</label>
                            <select
                                value={weatherOverlay}
                                onChange={(e) => setWeatherOverlay(e.target.value)}
                                className="bg-transparent text-xs text-cyan-400 font-medium focus:outline-none cursor-pointer"
                            >
                                <option value="none">Off</option>
                                <option value="precipitation">🌧 Precipitation</option>
                                <option value="temperature">🌡️ Temperature</option>
                                <option value="wind">💨 Wind Streamlines</option>
                                <option value="full">🌍 Full Weather</option>
                            </select>
                        </div>

                        {/* Simulation Control */}
                        <div className="flex items-center gap-2 bg-slate-800/50 rounded-lg px-2 py-1 border border-white/10">
                            <label className="text-xs text-slate-400">Ships/Port:</label>
                            <select
                                onChange={(e) => {
                                    // Send control message to backend
                                    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                                    const ws = new WebSocket(`${protocol}//localhost:8000/api/v1/ws/live-vessels`);
                                    ws.onopen = () => {
                                        ws.send(JSON.stringify({ type: 'UPDATE_COUNT', count: parseInt(e.target.value) }));
                                        ws.close();
                                    };
                                }}
                                className="bg-transparent text-xs text-cyan-400 font-mono focus:outline-none"
                                defaultValue="5"
                            >
                                <option value="5">5</option>
                                <option value="10">10</option>
                                <option value="20">20</option>
                                <option value="50">50</option>
                            </select>
                        </div>

                        <div className={`px-3 py-1 rounded-full text-xs font-mono border ${connectionStatus.includes('Connected') ? 'bg-green-500/20 border-green-500 text-green-300' : 'bg-red-500/20 border-red-500 text-red-300'
                            }`}>
                            ● {connectionStatus}
                        </div>
                        <div className="text-right">
                            <div className="text-2xl font-bold font-mono">{vesselList.length}</div>
                            <div className="text-xs text-slate-400 uppercase tracking-wider">Active Vessels</div>
                        </div>
                    </div>
                </header>

                <div className="flex-1 grid grid-cols-1 lg:grid-cols-4 gap-6 min-h-0">
                    {/* Stats Sidebar */}
                    <div className="lg:col-span-1 space-y-4 overflow-y-auto pr-2 custom-scrollbar">
                        {/* Summary Card */}
                        <div className="bg-white/5 border border-white/10 rounded-xl p-4 backdrop-blur-md">
                            <h2 className="text-sm font-semibold text-slate-300 mb-3 uppercase tracking-wider">Fleet ESG Health</h2>
                            <div className="grid grid-cols-2 gap-2">
                                <div className="bg-green-500/10 p-2 rounded text-center border border-green-500/20">
                                    <div className="text-xl font-bold text-green-400">
                                        {vesselList.filter(v => v.esg_score >= 90).length}
                                    </div>
                                    <div className="text-[10px] text-slate-400">Excellent</div>
                                </div>
                                <div className="bg-yellow-500/10 p-2 rounded text-center border border-yellow-500/20">
                                    <div className="text-xl font-bold text-yellow-400">
                                        {vesselList.filter(v => v.esg_score < 70 && v.esg_score >= 50).length}
                                    </div>
                                    <div className="text-[10px] text-slate-400">Moderate</div>
                                </div>
                            </div>
                        </div>

                        {/* Weather Impact Summary */}
                        <div className="bg-white/5 border border-white/10 rounded-xl p-4 backdrop-blur-md">
                            <h2 className="text-sm font-semibold text-slate-300 mb-3 uppercase tracking-wider">⛅ Weather Impact</h2>
                            <div className="space-y-2 text-xs text-slate-400">
                                {vesselList.length > 0 ? (
                                    <>
                                        <div className="flex justify-between">
                                            <span>Avg Wind:</span>
                                            <span className="text-cyan-300 font-semibold">
                                                {(vesselList.reduce((sum, v) => sum + (v.weather?.wind_speed_ms || 0), 0) / vesselList.length).toFixed(1)} m/s
                                            </span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span>Avg Waves:</span>
                                            <span className="text-cyan-300 font-semibold">
                                                {(vesselList.reduce((sum, v) => sum + (v.weather?.wave_height_m || 0), 0) / vesselList.length).toFixed(1)} m
                                            </span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span>Avg Resistance:</span>
                                            <span className={`font-semibold ${vesselList.reduce((sum, v) => sum + (v.weather?.weather_resistance_factor || 1), 0) / vesselList.length > 1.15 ? 'text-orange-400' : 'text-green-400'}`}>
                                                ×{(vesselList.reduce((sum, v) => sum + (v.weather?.weather_resistance_factor || 1), 0) / vesselList.length).toFixed(2)}
                                            </span>
                                        </div>
                                        <div className="flex justify-between pt-2 border-t border-slate-700">
                                            <span>Avg CO₂ Impact:</span>
                                            <span className="text-yellow-400 font-semibold">
                                                +{(vesselList.reduce((sum, v) => sum + (v.delta_weather || 0), 0) / vesselList.length).toFixed(0)} kg
                                            </span>
                                        </div>
                                    </>
                                ) : (
                                    <p className="text-slate-500">Waiting for data...</p>
                                )}
                            </div>
                        </div>

                        {/* Active List */}
                        <div className="bg-white/5 border border-white/10 rounded-xl p-4 backdrop-blur-md min-h-[300px]">
                            <h2 className="text-sm font-semibold text-slate-300 mb-3 uppercase tracking-wider">Latest Updates</h2>
                            <div className="space-y-2 text-xs">
                                {vesselList.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp)).slice(0, 8).map(v => (
                                    <div key={v.mmsi} className="p-2.5 bg-white/5 hover:bg-white/10 rounded border border-white/5 transition-colors">
                                        <div className="flex items-start justify-between mb-1">
                                            <div>
                                                <div className="font-medium text-sm text-cyan-300">{v.vessel_name}</div>
                                                <div className="text-slate-500 flex gap-1">
                                                    <span>{(v.speed_knots || v.speed || 0).toFixed(1)} kts</span>
                                                    <span className="text-slate-600">•</span>
                                                    <span>{v.sector || 'Unknown'}</span>
                                                </div>
                                            </div>
                                            <div className={`font-bold px-2 py-0.5 rounded ${v.esg_score >= 90 ? 'bg-green-500/20 text-green-300' :
                                                v.esg_score >= 70 ? 'bg-blue-500/20 text-blue-300' :
                                                v.esg_score >= 50 ? 'bg-yellow-500/20 text-yellow-300' :
                                                    'bg-red-500/20 text-red-300'
                                                }`}>
                                                {v.esg_score}
                                            </div>
                                        </div>
                                        
                                        {/* Weather Line */}
                                        {v.weather && (
                                            <div className="text-slate-400 flex gap-2 text-[10px] mb-1 py-1 px-1 bg-white/5 rounded border border-white/5">
                                                <span>💨 {v.weather.wind_speed_ms?.toFixed(1) || '0'} m/s</span>
                                                <span>🌊 {v.weather.wave_height_m?.toFixed(1) || '0'} m</span>
                                                <span className={`${v.weather.weather_resistance_factor > 1.2 ? 'text-orange-400' : 'text-green-400'}`}>
                                                    ⚡ ×{v.weather.weather_resistance_factor?.toFixed(2) || '1.00'}
                                                </span>
                                            </div>
                                        )}
                                        
                                        {/* Emissions Line */}
                                        {v.base_co2 && (
                                            <div className="text-slate-400 flex gap-2 text-[10px] px-1">
                                                <span className="text-blue-400">CO₂ Base: {v.base_co2?.toFixed(0)}</span>
                                                <span className={v.adjusted_co2 > v.base_co2 ? 'text-orange-400' : 'text-green-400'}>
                                                    Adj: {v.adjusted_co2?.toFixed(0)}
                                                </span>
                                                {v.delta_weather && (
                                                    <span className="text-yellow-400">
                                                        Δ +{v.delta_weather?.toFixed(0)}
                                                    </span>
                                                )}
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Main Map Area */}
                    <div className="lg:col-span-3 h-full rounded-xl overflow-hidden shadow-2xl border border-white/10 relative">
                        <LiveMap
                            vessels={vesselList}
                            center={sectors[selectedSector].center}
                            zoom={sectors[selectedSector].zoom}
                            weatherOverlay={weatherOverlay}
                        />

                        {/* Legend Overlay */}
                        <div className="absolute bottom-4 right-4 bg-slate-900/95 p-4 rounded-lg border border-white/20 backdrop-blur text-xs z-[1000] max-w-[240px]">
                            <div className="font-semibold mb-2 text-slate-300">ESG Status</div>
                            <div className="flex items-center gap-2 mb-1"><span className="w-2 h-2 rounded-full bg-green-500"></span> Excellent (90+)</div>
                            <div className="flex items-center gap-2 mb-1"><span className="w-2 h-2 rounded-full bg-blue-500"></span> Good (70-90)</div>
                            <div className="flex items-center gap-2 mb-3"><span className="w-2 h-2 rounded-full bg-yellow-500"></span> Moderate (50-70)</div>
                            
                            <div className="border-t border-slate-700 pt-2 mb-2">
                                <div className="font-semibold mb-2 text-slate-300">Weather Visualization</div>
                                
                                {(weatherOverlay === 'precipitation' || weatherOverlay === 'full') && (
                                    <div className="mb-2">
                                        <p className="font-semibold text-cyan-300 mb-1">🌧 Precipitation Radar:</p>
                                        <div className="space-y-0.5 text-[10px] text-slate-400">
                                            <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full" style={{backgroundColor: 'rgba(144,238,144,0.8)'}}></span> Clear</div>
                                            <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full" style={{backgroundColor: 'rgba(255,255,0,0.8)'}}></span> Light rain</div>
                                            <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full" style={{backgroundColor: 'rgba(255,165,0,0.8)'}}></span> Moderate</div>
                                            <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full" style={{backgroundColor: 'rgba(255,0,0,0.8)'}}></span> Heavy rain</div>
                                            <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full" style={{backgroundColor: 'rgba(186,0,231,0.8)'}}></span> Storm</div>
                                        </div>
                                    </div>
                                )}
                                
                                {(weatherOverlay === 'temperature' || weatherOverlay === 'full') && (
                                    <div className="mb-2">
                                        <p className="font-semibold text-cyan-300 mb-1">🌡️ Temperature Gradient:</p>
                                        <div className="space-y-0.5 text-[10px] text-slate-400">
                                            <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full" style={{backgroundColor: 'rgba(0,0,139,0.8)'}}></span> Very Cold (&lt;0°)</div>
                                            <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full" style={{backgroundColor: 'rgba(30,144,255,0.8)'}}></span> Cold (0-10°)</div>
                                            <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full" style={{backgroundColor: 'rgba(0,255,127,0.8)'}}></span> Cool (10-15°)</div>
                                            <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full" style={{backgroundColor: 'rgba(255,255,0,0.8)'}}></span> Warm (20°)</div>
                                            <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full" style={{backgroundColor: 'rgba(255,69,0,0.8)'}}></span> Hot (25°+)</div>
                                        </div>
                                    </div>
                                )}
                                
                                {(weatherOverlay === 'wind' || weatherOverlay === 'full') && (
                                    <div>
                                        <p className="font-semibold text-cyan-300 mb-1">💨 Wind Streamlines:</p>
                                        <p className="text-[10px] text-slate-400">→ Cyan animated particles<br/>→ Direction & intensity from wind data</p>
                                    </div>
                                )}
                            </div>

                            <div className="border-t border-slate-700 pt-2">
                                <div className="font-semibold mb-1 text-slate-300">CO₂ Emissions</div>
                                <div className="text-slate-400 space-y-1 text-[10px]">
                                    <p><span className="text-blue-300">Base</span> (no weather)</p>
                                    <p><span className="text-orange-300">Adjusted</span> (w/ weather)</p>
                                    <p><span className="text-yellow-300">Delta</span> (impact)</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default LiveTracking;
