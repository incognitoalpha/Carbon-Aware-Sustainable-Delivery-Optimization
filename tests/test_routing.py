import pytest
import os
import sys
from pathlib import Path
import networkx as nx
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.routing.osrm_client import OSRMClient
from src.routing.cost import edge_emission_cost, composite_cost
from src.routing.csp import find_route
from src.routing.batching import can_batch, prioritize_orders

def test_osrm_client():
    client = OSRMClient()
    route = client.get_route((18.9690, 72.8205), (18.9700, 72.8210))
    assert 'distance_m' in route
    assert 'duration_s' in route
    assert 'polyline' in route

def test_edge_emission_cost():
    edge_data = {
        'length': 1000.0,
        'speed_kph_peak': 20.0,
        'speed_kph_offpeak': 40.0
    }
    cost_peak = edge_emission_cost(edge_data, 'petrol_bike', 'peak')
    cost_offpeak = edge_emission_cost(edge_data, 'petrol_bike', 'offpeak')
    
    assert cost_peak > cost_offpeak

def test_csp_infeasible():
    # Create simple graph
    G = nx.DiGraph()
    G.add_edge(1, 2, length=5000.0, speed_kph_peak=20.0, speed_kph_offpeak=40.0)
    G.add_edge(2, 3, length=5000.0, speed_kph_peak=20.0, speed_kph_offpeak=40.0)
    
    # Tight budget
    route = find_route(G, 1, 3, 'petrol_bike', max_co2_budget_grams=10.0)
    assert route is None

    # Loose budget
    route = find_route(G, 1, 3, 'petrol_bike', max_co2_budget_grams=10000.0)
    assert route == [1, 2, 3]

def test_batching_edge_cases():
    now = datetime.now()
    order_A = {
        'pickup_lat': 18.9, 'pickup_lon': 72.8, 
        'deadline_at': now + timedelta(minutes=30)
    }
    
    # 1. 200m apart, 30 min deadline apart -> do not batch
    order_B_far_time = {
        'pickup_lat': 18.902, 'pickup_lon': 72.8, 
        'deadline_at': now + timedelta(minutes=60)
    }
    assert not can_batch(order_A, order_B_far_time)
    
    # 2. EV at 20% SoC offered long batch -> reject
    order_B_close = {
        'pickup_lat': 18.9, 'pickup_lon': 72.8, 
        'deadline_at': now + timedelta(minutes=35)
    }
    assert not can_batch(order_A, order_B_close, rider_soc=0.20, route_energy_cost=0.06)
    
    # Valid batch
    assert can_batch(order_A, order_B_close, rider_soc=0.50, route_energy_cost=0.06)

    # 3. Surge priority
    orders = [order_B_far_time, order_A]
    prioritized = prioritize_orders(orders, available_riders=1)
    assert prioritized[0] == order_A 
