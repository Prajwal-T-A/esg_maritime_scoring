import { useEffect, useRef } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';

/**
 * Advanced Weather Visualization Layer
 * Creates professional weather app-style visualizations:
 * - Precipitation heatmap (radar-style)
 * - Temperature gradient overlay
 * - Wind streamlines
 */

const AdvancedWeatherLayer = ({ vessels, overlayType = 'none' }) => {
    const map = useMap();
    const canvasLayerRef = useRef(null);
    const particlesRef = useRef([]);

    // Generate weather grid from vessel data
    const generateWeatherGrid = (vessels, gridSpacing = 0.1) => {
        if (!vessels || vessels.length === 0) return [];

        // Find bounds from vessels
        let minLat = 90, maxLat = -90, minLon = 180, maxLon = -180;
        vessels.forEach(v => {
            minLat = Math.min(minLat, v.latitude || v.lat);
            maxLat = Math.max(maxLat, v.latitude || v.lat);
            minLon = Math.min(minLon, v.longitude || v.lon);
            maxLon = Math.max(maxLon, v.longitude || v.lon);
        });

        // Expand bounds a bit
        minLat -= 0.2; maxLat += 0.2;
        minLon -= 0.2; maxLon += 0.2;

        // Create grid points
        const grid = [];
        for (let lat = minLat; lat <= maxLat; lat += gridSpacing) {
            for (let lon = minLon; lon <= maxLon; lon += gridSpacing) {
                // Interpolate weather from nearby vessels
                const nearestVessel = vessels.reduce((nearest, v) => {
                    const dist = Math.sqrt(
                        Math.pow(lat - (v.latitude || v.lat), 2) +
                        Math.pow(lon - (v.longitude || v.lon), 2)
                    );
                    return !nearest || dist < nearest.dist ? { ...v, dist } : nearest;
                }, null);

                if (nearestVessel && nearestVessel.weather) {
                    grid.push({
                        lat,
                        lon,
                        ...nearestVessel.weather,
                        distance: nearestVessel.dist
                    });
                }
            }
        }
        return grid;
    };

    // Map weather value to color for precipitation
    const getPrecipitationColor = (condition, waveHeight) => {
        const h = waveHeight || 0;
        const c = (condition || '').toLowerCase();

        // Return [R, G, B, A] format
        if (c.includes('thunderstorm') || c.includes('storm')) return [139, 0, 139, 200];    // Dark magenta
        if (h > 3) return [186, 0, 231, 180];                                                // Magenta
        if (h > 2 || c.includes('rain')) return [255, 0, 0, 160];                           // Red - heavy
        if (h > 1.5 || c.includes('drizzle')) return [255, 165, 0, 140];                    // Orange - moderate
        if (h > 1) return [255, 255, 0, 120];                                               // Yellow - light
        if (c.includes('cloud')) return [0, 191, 255, 100];                                 // Light blue - cloudy
        return [144, 238, 144, 80];                                                         // Light green - clear
    };

    // Map temperature to color
    const getTemperatureColor = (weatherData) => {
        // Simulated temp: use wave height as proxy (0-3m = 0-30°C)
        const temp = (weatherData.wave_height_m || 0) * 10;

        if (temp < 0) return [0, 0, 139, 180];           // Dark blue - very cold
        if (temp < 10) return [30, 144, 255, 180];       // Dodger blue - cold
        if (temp < 15) return [0, 255, 127, 160];        // Spring green - cool
        if (temp < 20) return [255, 255, 0, 140];        // Yellow - warm
        if (temp < 25) return [255, 165, 0, 140];        // Orange - hot
        if (temp < 30) return [255, 69, 0, 150];         // Red-orange - very hot
        return [139, 0, 0, 160];                          // Dark red - extreme
    };

    // Create canvas-based heatmap layer
    useEffect(() => {
        if (!map || overlayType === 'none') {
            if (canvasLayerRef.current) {
                map.removeLayer(canvasLayerRef.current);
                canvasLayerRef.current = null;
            }
            return;
        }

        // Remove old layer
        if (canvasLayerRef.current) {
            map.removeLayer(canvasLayerRef.current);
        }

        // Create canvas overlay
        const canvas = document.createElement('canvas');
        canvas.width = map.getSize().x;
        canvas.height = map.getSize().y;
        const ctx = canvas.getContext('2d');

        const weatherGrid = generateWeatherGrid(vessels, 0.15);

        // Draw based on type
        if (overlayType === 'precipitation' || overlayType === 'full') {
            weatherGrid.forEach(point => {
                const latLng = L.latLng(point.lat, point.lon);
                const point_px = map.latLngToLayerPoint(latLng);

                const [r, g, b, a] = getPrecipitationColor(point.condition, point.wave_height_m);

                // Draw circle with gradient
                ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${a / 255})`;
                ctx.beginPath();
                ctx.arc(point_px.x, point_px.y, 25, 0, Math.PI * 2);
                ctx.fill();
            });
        }

        if (overlayType === 'temperature' || overlayType === 'full') {
            weatherGrid.forEach(point => {
                const latLng = L.latLng(point.lat, point.lon);
                const point_px = map.latLngToLayerPoint(latLng);

                const [r, g, b, a] = getTemperatureColor(point);

                ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${a / 255})`;
                ctx.beginPath();
                ctx.arc(point_px.x, point_px.y, 20, 0, Math.PI * 2);
                ctx.fill();
            });
        }

        // Create canvas layer
        const canvasOverlay = L.imageOverlay(canvas.toDataURL(), map.getBounds(), {
            opacity: 0.5,
            zIndex: 200
        });

        canvasLayerRef.current = canvasOverlay;
        map.addLayer(canvasOverlay);

        // Redraw on map move/zoom
        const handleMapUpdate = () => {
            if (canvasLayerRef.current) {
                map.removeLayer(canvasLayerRef.current);
                canvas.width = map.getSize().x;
                canvas.height = map.getSize().y;
                const ctx = canvas.getContext('2d');

                if (overlayType === 'precipitation' || overlayType === 'full') {
                    weatherGrid.forEach(point => {
                        const latLng = L.latLng(point.lat, point.lon);
                        const point_px = map.latLngToLayerPoint(latLng);
                        const [r, g, b, a] = getPrecipitationColor(point.condition, point.wave_height_m);
                        ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${a / 255})`;
                        ctx.beginPath();
                        ctx.arc(point_px.x, point_px.y, 25, 0, Math.PI * 2);
                        ctx.fill();
                    });
                }

                if (overlayType === 'temperature' || overlayType === 'full') {
                    weatherGrid.forEach(point => {
                        const latLng = L.latLng(point.lat, point.lon);
                        const point_px = map.latLngToLayerPoint(latLng);
                        const [r, g, b, a] = getTemperatureColor(point);
                        ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${a / 255})`;
                        ctx.beginPath();
                        ctx.arc(point_px.x, point_px.y, 20, 0, Math.PI * 2);
                        ctx.fill();
                    });
                }

                const newOverlay = L.imageOverlay(canvas.toDataURL(), map.getBounds(), {
                    opacity: 0.5,
                    zIndex: 200
                });
                canvasLayerRef.current = newOverlay;
                map.addLayer(newOverlay);
            }
        };

        map.on('moveend', handleMapUpdate);
        map.on('zoomend', handleMapUpdate);

        return () => {
            map.off('moveend', handleMapUpdate);
            map.off('zoomend', handleMapUpdate);
            if (canvasLayerRef.current) {
                map.removeLayer(canvasLayerRef.current);
            }
        };
    }, [map, vessels, overlayType]);

    // Wind streamlines effect
    useEffect(() => {
        if (!map || (overlayType !== 'wind' && overlayType !== 'full')) {
            return;
        }

        // Create animated wind particles
        const canvas = document.createElement('canvas');
        canvas.width = map.getSize().x;
        canvas.height = map.getSize().y;
        canvas.style.position = 'absolute';
        canvas.style.zIndex = '250';
        canvas.style.top = '0';
        canvas.style.left = '0';

        // Initialize particles
        particlesRef.current = [];
        vessels.forEach(v => {
            if (v.weather && v.weather.wind_speed_ms > 0) {
                const latLng = L.latLng(v.latitude || v.lat, v.longitude || v.lon);
                const point_px = map.latLngToLayerPoint(latLng);

                for (let i = 0; i < 15; i++) {
                    particlesRef.current.push({
                        x: point_px.x + (Math.random() - 0.5) * 60,
                        y: point_px.y + (Math.random() - 0.5) * 60,
                        vx: Math.cos((v.weather.wind_direction_deg * Math.PI) / 180) * (v.weather.wind_speed_ms * 2),
                        vy: Math.sin((v.weather.wind_direction_deg * Math.PI) / 180) * (v.weather.wind_speed_ms * 2),
                        life: Math.random() * 100 + 50,
                        maxLife: 150,
                        mapWidth: map.getSize().x,
                        mapHeight: map.getSize().y
                    });
                }
            }
        });

        let animationId;
        const ctx = canvas.getContext('2d');

        const animate = () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            particlesRef.current = particlesRef.current.filter(p => p.life > 0);

            particlesRef.current.forEach(p => {
                p.x += p.vx;
                p.y += p.vy;
                p.life -= 2;

                const opacity = (p.life / p.maxLife) * 0.7;
                ctx.strokeStyle = `rgba(0, 212, 255, ${opacity})`;
                ctx.lineWidth = 2;

                ctx.beginPath();
                ctx.moveTo(p.x, p.y);
                ctx.lineTo(p.x - p.vx * 0.5, p.y - p.vy * 0.5);
                ctx.stroke();
            });

            // Wrap around edges
            particlesRef.current.forEach(p => {
                if (p.x < 0) p.x = p.mapWidth;
                if (p.x > p.mapWidth) p.x = 0;
                if (p.y < 0) p.y = p.mapHeight;
                if (p.y > p.mapHeight) p.y = 0;
            });

            animationId = requestAnimationFrame(animate);
        };

        const mapPane = map.getPanes().overlayPane;
        mapPane.appendChild(canvas);
        animate();

        return () => {
            cancelAnimationFrame(animationId);
            mapPane.removeChild(canvas);
        };
    }, [map, vessels, overlayType]);

    return null;
};

export default AdvancedWeatherLayer;
