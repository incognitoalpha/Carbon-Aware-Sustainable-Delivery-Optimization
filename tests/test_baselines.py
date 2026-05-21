import pytest
import os
import sys
from pathlib import Path
import networkx as nx

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.baselines.shortest_time import evaluate_shortest_time
from src.baselines.emission_weighted import evaluate_emission_weighted
from src.baselines.heuristic_batching import heuristic_batching
from src.routing.csp import find_route
from src.eval.compare import generate_comparison_table

def test_shortest_time():
    orders = [
        {'order_id': 1, 'pickup_lat': 18.9, 'pickup_lon': 72.8, 'dropoff_lat': 18.91, 'dropoff_lon': 72.81}
    ]
    results = evaluate_shortest_time(orders)
    assert len(results) == 1
    assert results[0]['co2_per_order_g'] > 0

def test_emission_weighted():
    G = nx.DiGraph()
    G.add_node(1)
    G.add_node(2)
    G.add_edge(1, 2, length=1000.0, speed_kph_peak=20.0, speed_kph_offpeak=40.0)
    
    orders = [{'order_id': 1}]
    results = evaluate_emission_weighted(G, orders, 'petrol_bike')
    assert len(results) == 1
    assert results[0]['co2_per_order_g'] > 0

def test_csp_infeasibility():
    G = nx.DiGraph()
    G.add_edge(1, 2, length=5000.0, speed_kph_peak=20.0, speed_kph_offpeak=40.0)
    G.add_edge(2, 3, length=5000.0, speed_kph_peak=20.0, speed_kph_offpeak=40.0)
    
    # Infeasibility test: very tight budget
    route = find_route(G, 1, 3, 'petrol_bike', max_co2_budget_grams=5.0)
    assert route is None

def test_compare_script():
    generate_comparison_table()
    assert os.path.exists("results/baseline_comparison.csv")
    
    import pandas as pd
    df = pd.read_csv("results/baseline_comparison.csv")
    assert df.isnull().sum().sum() == 0 # no NaN values
