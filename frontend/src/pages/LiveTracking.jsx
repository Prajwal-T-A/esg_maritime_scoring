
import React, { useEffect, useState, useRef } from 'react';
import LiveMap from '../components/LiveMap';

const sectors = {
    Singapore: { center: [1.290270, 103.851959], zoom: 10 },
    India: { center: [18.9667, 72.8333], zoom: 9 } // Mumbai center
};

const LiveTracking = () => {
    const [vessels, setVessels] = useState({});
    const [connectionStatus, setConnectionStatus] = useState('Connecting...');
    const [selectedSector, setSelectedSector] = useState('Singapore');

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
                            </select>
                            <p className="text-slate-400 text-xs text-slate-500">
                                • Real-time ESG monitoring
                            </p>
                        </div>
                    </div>
                    <div className="flex items-center gap-4">
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

                        {/* Active List */}
                        <div className="bg-white/5 border border-white/10 rounded-xl p-4 backdrop-blur-md min-h-[300px]">
                            <h2 className="text-sm font-semibold text-slate-300 mb-3 uppercase tracking-wider">Latest Updates</h2>
                            <div className="space-y-2">
                                {vesselList.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp)).slice(0, 8).map(v => (
                                    <div key={v.mmsi} className="flex items-center justify-between p-2 bg-white/5 hover:bg-white/10 rounded border border-white/5 transition-colors">
                                        <div>
                                            <div className="font-medium text-sm text-cyan-300">{v.vessel_name}</div>
                                            <div className="text-xs text-slate-500 flex gap-2">
                                                <span>{v.speed.toFixed(1)} kts</span>
                                                <span className="text-slate-600">|</span>
                                                <span>{v.sector || 'Unknown'}</span>
                                            </div>
                                        </div>
                                        <div className={`text-xs font-bold px-2 py-1 rounded ${v.esg_score >= 90 ? 'bg-green-500/20 text-green-300' :
                                            v.esg_score >= 50 ? 'bg-yellow-500/20 text-yellow-300' :
                                                'bg-red-500/20 text-red-300'
                                            }`}>
                                            {v.esg_score}
                                        </div>
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
                        />

                        {/* Legend Overlay */}
                        <div className="absolute bottom-4 right-4 bg-slate-900/90 p-3 rounded-lg border border-white/20 backdrop-blur text-xs z-[1000]">
                            <div className="font-semibold mb-2 text-slate-300">ESG Status</div>
                            <div className="flex items-center gap-2 mb-1"><span className="w-2 h-2 rounded-full bg-green-500"></span> Excellent (90+)</div>
                            <div className="flex items-center gap-2 mb-1"><span className="w-2 h-2 rounded-full bg-yellow-500"></span> Moderate (50-70)</div>
                            <div className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-red-500"></span> Critical (&lt;30)</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default LiveTracking;
