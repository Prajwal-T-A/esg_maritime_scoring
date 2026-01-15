import React from 'react';

/**
 * Weather Overlay Component
 * Displays weather information as an overlay on the map
 */
const WeatherOverlay = ({ vessels, mode }) => {
    if (mode === 'none' || !vessels || vessels.length === 0) {
        return null;
    }

    // Filter vessels with valid weather data
    const vesselsWithWeather = vessels.filter(v => v.weather && v.weather.wind_speed_ms !== undefined);
    
    if (vesselsWithWeather.length === 0) {
        return (
            <div className="absolute top-4 left-4 bg-slate-900/90 backdrop-blur-md rounded-lg border border-white/20 p-4 z-[1000] max-w-xs">
                <h3 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
                    <span>☁️</span> Weather Conditions
                </h3>
                <div className="text-xs text-slate-500">Loading weather data...</div>
            </div>
        );
    }

    // Calculate average weather metrics
    const avgWind = vesselsWithWeather.reduce((sum, v) => sum + v.weather.wind_speed_ms, 0) / vesselsWithWeather.length;
    const avgWaves = vesselsWithWeather.reduce((sum, v) => sum + v.weather.wave_height_m, 0) / vesselsWithWeather.length;
    const avgTemp = vesselsWithWeather.reduce((sum, v) => sum + (v.weather.temperature_c || 20), 0) / vesselsWithWeather.length;
    const hasStorm = vesselsWithWeather.some(v => v.weather.storm_flag);
    const roughSeas = vesselsWithWeather.filter(v => v.weather.rough_sea_flag).length;

    return (
        <div className="absolute top-4 left-4 bg-slate-900/90 backdrop-blur-md rounded-lg border border-white/20 p-4 z-[1000] max-w-xs">
            <h3 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
                <span>☁️</span> Weather Conditions
            </h3>
            
            <div className="space-y-2 text-xs">
                {(mode === 'wind' || mode === 'full') && (
                    <div className="flex items-center justify-between p-2 bg-white/5 rounded">
                        <span className="text-slate-400">Wind Speed:</span>
                        <span className="text-cyan-400 font-mono font-bold">{avgWind.toFixed(1)} m/s</span>
                    </div>
                )}
                
                {(mode === 'full') && (
                    <div className="flex items-center justify-between p-2 bg-white/5 rounded">
                        <span className="text-slate-400">Wave Height:</span>
                        <span className="text-blue-400 font-mono font-bold">{avgWaves.toFixed(1)} m</span>
                    </div>
                )}
                
                {(mode === 'temperature' || mode === 'full') && (
                    <div className="flex items-center justify-between p-2 bg-white/5 rounded">
                        <span className="text-slate-400">Temperature:</span>
                        <span className="text-orange-400 font-mono font-bold">{avgTemp.toFixed(1)}°C</span>
                    </div>
                )}
                
                {(mode === 'precipitation' || mode === 'full') && (
                    <div className="flex items-center justify-between p-2 bg-white/5 rounded">
                        <span className="text-slate-400">Conditions:</span>
                        <span className={`font-bold ${hasStorm ? 'text-red-400' : roughSeas > 0 ? 'text-yellow-400' : 'text-green-400'}`}>
                            {hasStorm ? '⛈️ Storm' : roughSeas > 0 ? '🌊 Rough' : '✓ Calm'}
                        </span>
                    </div>
                )}
                
                {mode === 'full' && (
                    <>
                        <div className="border-t border-white/10 my-2 pt-2">
                            <div className="text-[10px] text-slate-500 uppercase tracking-wider mb-1">Alerts</div>
                            {hasStorm && (
                                <div className="px-2 py-1 bg-red-500/20 text-red-300 rounded text-[10px] mb-1">
                                    ⚠️ Storm Warning Active
                                </div>
                            )}
                            {roughSeas > 0 && (
                                <div className="px-2 py-1 bg-orange-500/20 text-orange-300 rounded text-[10px] mb-1">
                                    🌊 {roughSeas} Vessel{roughSeas > 1 ? 's' : ''} in Rough Seas
                                </div>
                            )}
                            {!hasStorm && roughSeas === 0 && (
                                <div className="px-2 py-1 bg-green-500/20 text-green-300 rounded text-[10px]">
                                    ✓ Normal Conditions
                                </div>
                            )}
                        </div>
                        
                        <div className="border-t border-white/10 mt-2 pt-2">
                            <div className="text-[10px] text-slate-500 uppercase tracking-wider mb-1">Weather Impact</div>
                            <div className="flex items-center justify-between">
                                <span className="text-slate-400">Avg CO₂ Increase:</span>
                                <span className="text-yellow-400 font-mono font-bold">
                                    +{(() => {
                                        const validVessels = vessels.filter(v => v.delta_weather !== undefined);
                                        const avg = validVessels.length > 0 ? validVessels.reduce((sum, v) => sum + v.delta_weather, 0) / validVessels.length : 0;
                                        return avg.toFixed(0);
                                    })()} kg
                                </span>
                            </div>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
};

export default WeatherOverlay;
