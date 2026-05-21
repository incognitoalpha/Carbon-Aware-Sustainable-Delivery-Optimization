import os
import json
import pytest
import pandas as pd
import networkx as nx
import osmnx as ox
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.simulator.order_generator import generate_orders
from src.data.weather import WeatherStub

def test_osm_graph_properties():
    assert os.path.exists("data/processed/graph_with_speeds.graphml")
    G = ox.load_graphml("data/processed/graph_with_speeds.graphml")
    assert len(G.nodes) >= 1000
    
    # Check speed attributes
    for u, v, k, data in G.edges(keys=True, data=True):
        assert 'speed_kph_peak' in data
        assert 'speed_kph_offpeak' in data
        break

def test_order_generator_deterministic():
    generate_orders(seed=42, num_days=2, base_orders_per_day=100)
    assert os.path.exists("data/synthetic/orders_42.parquet")
    
    df1 = pd.read_parquet("data/synthetic/orders_42.parquet")
    generate_orders(seed=42, num_days=2, base_orders_per_day=100)
    df2 = pd.read_parquet("data/synthetic/orders_42.parquet")
    
    pd.testing.assert_frame_equal(df1, df2)

def test_fleet_schema():
    assert os.path.exists("data/processed/fleet.json")
    with open("data/processed/fleet.json", "r") as f:
        fleet = json.load(f)
        
    assert isinstance(fleet, list)
    for vehicle in fleet:
        assert 'type' in vehicle
        assert 'co2_per_km_grams' in vehicle
        assert 'speed_factor' in vehicle

def test_splits_non_overlapping():
    assert os.path.exists("data/processed/splits.json")
    with open("data/processed/splits.json", "r") as f:
        splits = json.load(f)
        
    train_set = set(splits['train'])
    val_set = set(splits['val'])
    test_set = set(splits['test'])
    
    assert train_set.isdisjoint(val_set)
    assert val_set.isdisjoint(test_set)
    assert train_set.isdisjoint(test_set)

def test_weather_stub():
    weather = WeatherStub()
    temp, precip = weather.get_weather(datetime(2026, 1, 1, 12, 30))
    assert isinstance(temp, float)
    assert precip in [0, 1]
