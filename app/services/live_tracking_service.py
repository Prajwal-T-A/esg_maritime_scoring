
import asyncio
import json
import logging
import random
import os
import websockets
from datetime import datetime, timezone
from typing import Dict, List, Optional
from app.services.ml_service import predict_emissions
from app.config import settings

logger = logging.getLogger(__name__)

class LiveTrackingService:
    def __init__(self):
        self.api_key = os.getenv("AISSTREAM_API_KEY")
        self.connected_clients = set()
        self.is_running = False
        # Sectors: Singapore Strait and Mumbai Coast (India)
        # Format: [[Lon, Lat], [Lon, Lat]]
        self.sectors = {
            "Singapore": [[[103.5, 1.1], [104.1, 1.5]]],
            "India": [[[72.5, 18.8], [73.0, 19.2]]], # Mumbai / JNPT approaches
            "Visakhapatnam": [[[83.2, 17.6], [83.4, 17.8]]], # Visakhapatnam Port
            "Mangalore": [[[74.7, 12.8], [74.9, 13.0]]] # New Mangalore Port
        }
        # Combine all sectors for the subscription
        self.bounding_box = [box[0] for box in self.sectors.values()]

    async def broadcast_to_clients(self, message: dict):
        """Send message to all connected WebSocket clients."""
        if not self.connected_clients:
            return
            
        disconnected_clients = set()
        for client in self.connected_clients:
            try:
                await client.send_json(message)
            except Exception:
                disconnected_clients.add(client)
        
        for client in disconnected_clients:
            self.connected_clients.remove(client)

    async def connect_client(self, websocket):
        """Register a new client connection."""
        await websocket.accept()
        self.connected_clients.add(websocket)
        logger.info(f"Client connected. Total clients: {len(self.connected_clients)}")

    def disconnect_client(self, websocket):
        """Unregister a client connection."""
        self.connected_clients.discard(websocket)
        logger.info(f"Client disconnected. Total clients: {len(self.connected_clients)}")

    async def _calculate_projected_analysis(self, mmsi: str, speed: float) -> dict:
        """
        Use the shared Analysis Service to get a valid ESG score.
        Projects the current snapshot into a 24-hour voyage to satisfy model requirements.
        """
        try:
            # 1. Project metrics for 24-hour "Day-in-the-Life"
            duration_hours = 24.0
            projected_distance = speed * 1.852 * duration_hours # km
            
            # Default Panamax parameters
            length = 225.0
            width = 32.0
            draft = 12.0
            
            # 2. Call the Unified Analysis Service
            # This uses the EXACT same random forest model as the /analyze endpoint
            from app.services.analysis_service import analyze_vessel
            
            result = await analyze_vessel(
                mmsi=mmsi,
                avg_speed=speed,
                speed_std=0.5 + (random.random() * 0.5), # Slight noise for realism
                total_distance_km=projected_distance,
                time_at_sea_hours=duration_hours,
                acceleration_events=int(speed / 4),
                length=length,
                width=width,
                draft=draft,
                co2_factor=3.114,
                include_ai_recommendation=False # Skip Ollama for speed
            )
            
            # Debugging
            print(f"[LIVE-ML] Vessel {mmsi} | Speed {speed:.1f} | Score {result['esg_score']}")
            
            # Map result to color
            score = result['esg_score']
            color = "green"
            if score < 90: color = "blue"
            if score < 70: color = "yellow"
            if score < 50: color = "orange"
            if score < 30: color = "red"
            if score >= 70: color = "green" # Standardize
            
            return {"score": score, "color": color, "risk_flags": result['risk_flags']}

        except Exception as e:
            print(f"[LIVE-ERROR] Analysis failed: {e}")
            return self._calculate_instant_esg_fallback(speed)

    def _calculate_instant_esg_fallback(self, speed: float) -> dict:
        """Fallback simple scoring if ML service is unavailable."""
        score = 99 # Distinct value identifying fallback
        if speed > 14.0: score -= 20
        if speed > 18.0: score -= 30
        
        color = "green"
        if score < 70: color = "yellow"
        if score < 50: color = "red"
        return {"score": score, "color": color, "risk_flags": ["Model Unavailable"]}

    async def stream_ais_data(self):
        """Standard streaming with control message handling."""
        self.is_running = True
        
        # If no API key, start simulation directly
        if not self.api_key:
            logger.warning("No AISSTREAM_API_KEY found. Starting simulation mode.")
            await self._run_simulation()
            return

        async with websockets.connect("wss://stream.aisstream.io/v0/stream") as ws:
            subscribe_message = {
                "APIKey": self.api_key,
                "BoundingBoxes": self.bounding_box,
                "FiltersShipMMSI": None,
                "FilterMessageTypes": ["PositionReport"] 
            }
            await ws.send(json.dumps(subscribe_message))
            
            async for message_json in ws:
                if not self.is_running:
                    break
                    
                try:
                    message = json.loads(message_json)
                    if "PositionReport" in message.get("MessageType", ""):
                        report = message["Message"]["PositionReport"]
                        mmsi = str(report["UserID"])
                        lat = report["Latitude"]
                        lon = report["Longitude"]
                        speed = report.get("Sog", 0.0)
                        heading = report.get("Cog", 0.0)
                        
                        # USE SHARED ANALYSIS SERVICE
                        esg = await self._calculate_projected_analysis(mmsi, speed)
                        
                        # Determine rough sector for display context if needed
                        sector = "Unknown"
                        if 103.5 <= lon <= 104.1 and 1.1 <= lat <= 1.5: sector = "Singapore"
                        elif 72.5 <= lon <= 73.0 and 18.8 <= lat <= 19.2: sector = "India"
                        elif 83.2 <= lon <= 83.4 and 17.6 <= lat <= 17.8: sector = "Visakhapatnam"
                        elif 74.7 <= lon <= 74.9 and 12.8 <= lat <= 13.0: sector = "Mangalore"

                        processed_msg = {
                            "mmsi": mmsi,
                            "lat": lat,
                            "lon": lon,
                            "speed": speed,
                            "heading": heading,
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "esg_score": esg["score"],
                            "esg_color": esg["color"],
                            "vessel_name": f"Vessel {mmsi[-4:]}",
                            "sector": sector,
                            "risk_flags": esg["risk_flags"]
                        }
                        
                        await self.broadcast_to_clients(processed_msg)
                        
                except Exception as e:
                    logger.error(f"Error processing AIS message: {e}")
                    await asyncio.sleep(1)

    async def handle_client_message(self, message: str):
        """Process control messages from frontend."""
        try:
            data = json.loads(message)
            if data.get('type') == 'UPDATE_COUNT':
                new_count = int(data.get('count', 5))
                self.simulation_count = new_count
                logger.info(f"Updated simulation vessel count to {new_count} per port")
                # Restart simulation with new count if already running in sim mode
                if self.is_simulation_active:
                     self.should_restart_simulation = True
        except Exception as e:
            logger.error(f"Error handling client message: {e}")

    async def _run_simulation(self):
        """Generate fake vessel movements."""
        self.is_simulation_active = True
        self.simulation_count = getattr(self, 'simulation_count', 5) # Default to 5
        
        while self.is_running:
            self.should_restart_simulation = False
            vessels = []
            
            # Generate vessels based on current count
            # Singapore
            for i in range(self.simulation_count):
                vessels.append({
                    "mmsi": f"563{i:03d}",
                    "lat": 1.25 + (random.random() - 0.5) * 0.1,
                    "lon": 103.8 + (random.random() - 0.5) * 0.2,
                    "speed": 10.0 + random.random() * 10.0,
                    "course": random.random() * 360,
                    "name": f"SG Lion {i+1}",
                    "sector": "Singapore"
                })
            # India
            for i in range(self.simulation_count):
                vessels.append({
                    "mmsi": f"419{i:03d}",
                    "lat": 18.9 + (random.random() - 0.5) * 0.1,
                    "lon": 72.8 + (random.random() - 0.5) * 0.1,
                    "speed": 8.0 + random.random() * 8.0,
                    "course": random.random() * 360,
                    "name": f"IND Sagar {i+1}",
                    "sector": "India"
                })
            # Visakhapatnam
            for i in range(self.simulation_count):
                 vessels.append({
                    "mmsi": f"419{i+500:03d}", # Distinct MMSI range
                    "lat": 17.7 + (random.random() - 0.5) * 0.05,
                    "lon": 83.3 + (random.random() - 0.5) * 0.05,
                    "speed": 5.0 + random.random() * 5.0,
                    "course": random.random() * 360,
                    "name": f"VSKP Port {i+1}",
                    "sector": "Visakhapatnam"
                })
            # Mangalore
            for i in range(self.simulation_count):
                 vessels.append({
                    "mmsi": f"419{i+800:03d}",
                    "lat": 12.9 + (random.random() - 0.5) * 0.05,
                    "lon": 74.8 + (random.random() - 0.5) * 0.05,
                    "speed": 6.0 + random.random() * 6.0,
                    "course": random.random() * 360,
                    "name": f"NMPT Port {i+1}",
                    "sector": "Mangalore"
                })

            while self.is_running and not self.should_restart_simulation:
                for v in vessels:
                    # Update physics
                    direction_lat = 1 if v["course"] < 180 else -1
                    direction_lon = 1 if 90 < v["course"] < 270 else -1
                    v["lat"] += (random.random() * 0.001) * direction_lat
                    v["lon"] += (random.random() * 0.001) * direction_lon
                    v["speed"] = max(0, min(25, v["speed"] + (random.random() - 0.5)))
                    
                    try:
                        esg = await self._calculate_projected_analysis(v["mmsi"], v["speed"])
                    except Exception:
                        esg = self._calculate_instant_esg_fallback(v["speed"])
                    
                    msg = {
                        "mmsi": v["mmsi"],
                        "lat": v["lat"],
                        "lon": v["lon"],
                        "speed": round(v["speed"], 1),
                        "heading": round(v["course"], 1),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "esg_score": esg["score"],
                        "esg_color": esg["color"],
                        "vessel_name": v["name"],
                        "sector": v["sector"],
                        "risk_flags": esg["risk_flags"],
                        "is_simulation": True
                    }
                    await self.broadcast_to_clients(msg)
                
                await asyncio.sleep(2)

live_tracking_service = LiveTrackingService()
