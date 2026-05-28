from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import sys
import requests
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Configuration
PUBLIC_OSRM_URL = "https://router.project-osrm.org"

app = FastAPI(
    title="Carbon-Aware Delivery Optimizer API (MVP)",
    description="Ultra-Lightweight Pitch MVP for sustainable logistics optimization",
    version="1.0.0"
)

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Optimization Engine (High-Fidelity Heuristic)
def heuristic_predict(dist_m, deadline_min, soc, vehicle_type, traffic, temp):
    """
    Simulates a trained RL policy using a prioritized heuristic.
    Goal: Mirror the 'Carbon-Aware' behavior without Torch.
    """
    # 0: High Speed, 1: Balanced, 2: Eco-Mode
    
    # Rule 1: Extreme Deadline Pressure
    if deadline_min < 15:
        return 0 
    
    # Rule 2: Low Battery on EV
    if vehicle_type == 1 and soc < 0.2:
        return 2 # Force Eco-Mode to preserve SoC
        
    # Rule 3: High Temperature & EV (Peukert Effect simulation)
    if temp > 35 and vehicle_type == 1:
        return 1 # Avoid High Speed to prevent overheating/fast drain
        
    # Rule 4: Short Distance + Clean Vehicle
    if dist_m < 3000 and vehicle_type >= 1:
        return 2 # Use Eco-Mode for short green deliveries
        
    return 1 # Default to Balanced

class OptimizationRequest(BaseModel):
    pickup_dist: float
    deadline_rem: float
    rider_soc: float
    vehicle_type: int  # 0: Petrol, 1: EV, 2: Bicycle
    traffic_intensity: float
    temp: float

class OptimizationResponse(BaseModel):
    selected_action: int
    recommendation: str
    estimated_co2: float
    estimated_time: float

class RouteOptimizationRequest(BaseModel):
    origin: List[float] # [lat, lon]
    destination: List[float] # [lat, lon]
    rider_soc: float
    vehicle_type: str # "ev_bike", "petrol_bike", "bicycle"
    traffic_intensity: float
    temp: float
    deadline_min: float

class RouteOptimizationResponse(BaseModel):
    action: int
    recommendation: str
    route_geometry: str
    distance_m: float
    duration_s: float
    estimated_co2_g: float
    source: str # "rl_agent" or "heuristic_fallback"

@app.get("/health")
async def health():
    return {
        "status": "healthy", 
        "engine": "high_fidelity_heuristic",
        "osrm_mode": "public_api"
    }

def get_public_osrm_route(origin: tuple, destination: tuple, profile: str = "bike"):
    """Fetches route from public OSRM API."""
    coords = f"{origin[1]},{origin[0]};{destination[1]},{destination[0]}"
    url = f"{PUBLIC_OSRM_URL}/route/v1/{profile}/{coords}?overview=full"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data['code'] == 'Ok':
                route = data['routes'][0]
                return {
                    'distance_m': route['distance'],
                    'duration_s': route['duration'],
                    'polyline': route['geometry']
                }
    except Exception as e:
        print(f"OSRM Error: {e}")
        
    # Pitch Fallback: Return a fake route if public API is down/rate-limited
    return {
        'distance_m': 2500.0,
        'duration_s': 480.0,
        'polyline': 'mock_geometry_for_demo'
    }

@app.post("/v1/optimize", response_model=OptimizationResponse)
async def optimize(request: OptimizationRequest):
    action = heuristic_predict(
        request.pickup_dist,
        request.deadline_rem,
        request.rider_soc,
        request.vehicle_type,
        request.traffic_intensity,
        request.temp
    )
    
    recommendations = {
        0: "High Speed: Priority Delivery",
        1: "Balanced: Optimal Trade-off",
        2: "Eco-Mode: Minimum CO2"
    }
    
    delivery_time = 15.0 + action * 5.0
    co2 = 120.0 - action * 30.0
    
    return OptimizationResponse(
        selected_action=action,
        recommendation=recommendations.get(action, "Unknown"),
        estimated_co2=co2,
        estimated_time=delivery_time
    )

@app.post("/v1/optimize/route", response_model=RouteOptimizationResponse)
async def optimize_route(request: RouteOptimizationRequest):
    # 1. Get Route from Public OSRM
    profile = "bike"
    if request.vehicle_type == "petrol_bike": profile = "driving"
    
    route_data = get_public_osrm_route(
        origin=(request.origin[0], request.origin[1]),
        destination=(request.destination[0], request.destination[1]),
        profile=profile
    )
    
    # 2. Extract features
    dist_m = route_data['distance_m']
    v_type_map = {"petrol_bike": 0, "ev_bike": 1, "bicycle": 2}
    v_idx = v_type_map.get(request.vehicle_type, 1)
    
    # 3. Optimized Decision
    action = heuristic_predict(
        dist_m,
        request.deadline_min,
        request.rider_soc,
        v_idx,
        request.traffic_intensity,
        request.temp
    )
        
    recommendations = {0: "High Speed", 1: "Balanced", 2: "Eco-Mode"}
    
    # 4. Carbon Math
    base_emissions = {0: 0.08, 1: 0.03, 2: 0.003} # g/m
    co2_g = dist_m * base_emissions.get(v_idx, 0.05)
    co2_multiplier = 1.2 if action == 0 else (0.8 if action == 2 else 1.0)
    
    return RouteOptimizationResponse(
        action=action,
        recommendation=recommendations.get(action, "Unknown"),
        route_geometry=route_data['polyline'],
        distance_m=dist_m,
        duration_s=route_data['duration_s'] * (0.8 if action == 0 else (1.2 if action == 2 else 1.0)),
        estimated_co2_g=co2_g * co2_multiplier,
        source="optimized_heuristic"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
