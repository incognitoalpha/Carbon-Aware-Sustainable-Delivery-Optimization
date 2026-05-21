import pytest
import sys
import os
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.simulator.city_sim import CitySimulator
from src.simulator.metrics import log_metrics

def test_city_simulator():
    orders = [{'order_id': i} for i in range(100)]
    fleet = [{'type': 'ev_bike'}]
    
    config = {'soc_constraint_enabled': True}
    sim = CitySimulator(config, orders, fleet)
    sim.run(until=86400 / 60.0)
    
    assert len(sim.unassigned_orders) == 0
    assert len(sim.delivered_orders) == 100
    assert sim.ev_battery_violations == 0
    
    config_disabled = {'soc_constraint_enabled': False}
    sim2 = CitySimulator(config_disabled, orders, fleet)
    sim2.run(until=86400 / 60.0)
    
    assert sim2.ev_battery_violations > 0

def test_metrics_logger():
    metrics = [
        {'order_id': 1, 'delivery_time_min': 20.0, 'co2_per_order_g': 100.0, 'is_sla_breach': False}
    ]
    log_metrics(metrics, "dense_urban", "ppo", 42)
    
    file_path = "results/sim_dense_urban_ppo_42.parquet"
    assert os.path.exists(file_path)
    
    df = pd.read_parquet(file_path)
    assert len(df) == 1
    assert 'co2_per_order_g' in df.columns
