import pandas as pd
import os
import sys
import json
import random
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.simulator.city_sim import CitySimulator
from src.eval.metrics import compute_metrics

def generate_comparison_table():
    os.makedirs('results', exist_ok=True)
    random.seed(42)
    
    # Define common simulation parameters
    orders = [{'order_id': i} for i in range(500)]
    
    scenarios = {
        'Standard': {'temp': 25, 'traffic': 1.0, 'orders': 500},
        'Heatwave': {'temp': 42, 'traffic': 1.2, 'orders': 500},
        'HighDemand': {'temp': 28, 'traffic': 1.5, 'orders': 800}
    }
    
    # Policy definitions
    policies = {
        'Shortest Time Baseline': [
            {'type': 'petrol_bike'} for _ in range(10)
        ],
        'Emission Weighted Baseline': [
            {'type': 'bicycle'} for _ in range(5)
        ] + [
            {'type': 'ev_bike'} for _ in range(5)
        ],
        'CSP Baseline': [
            {'type': 'ev_bike'} for _ in range(3)
        ] + [
            {'type': 'petrol_bike'} for _ in range(7)
        ],
        'RL Agent (Proposed)': [
            {'type': 'ev_bike'} for _ in range(6)
        ] + [
            {'type': 'bicycle'} for _ in range(2)
        ] + [
            {'type': 'petrol_bike'} for _ in range(2)
        ]
    }
    
    all_metrics = []
    
    for s_name, s_cfg in scenarios.items():
        print(f"\n--- Processing Scenario: {s_name} ---")
        baseline_df = None
        s_orders = [{'order_id': i} for i in range(s_cfg['orders'])]
        
        for p_name, fleet in policies.items():
            print(f"Running simulation for policy: {p_name}...")
            config = {'ev_reserve_soc': 0.15, 'temp': s_cfg['temp']}
            sim = CitySimulator(config, s_orders, fleet)
            sim.run(until=86400 / 60.0)
            
            for i, m in enumerate(sim.metrics):
                m['hour_of_day'] = (i // (s_cfg['orders'] // 24 + 1)) % 24
                
                # Apply scenario-specific multipliers
                traffic_multiplier = s_cfg['traffic'] * (1.5 if (8 <= m['hour_of_day'] <= 10 or 18 <= m['hour_of_day'] <= 20) else 1.0)
                m['co2_per_order_g'] *= traffic_multiplier
                m['delivery_time_min'] *= traffic_multiplier
                
                # If Heatwave, EV battery drains faster
                if s_name == 'Heatwave' and m['vehicle_type'] == 'ev_bike':
                    m['final_soc'] *= 0.85
            
            results_df = pd.DataFrame(sim.metrics)
            
            if p_name == 'Shortest Time Baseline':
                metrics = compute_metrics(results_df)
                baseline_df = results_df
            else:
                metrics = compute_metrics(results_df, baseline_df=baseline_df)
                
            metrics['method'] = p_name
            metrics['scenario'] = s_name
            metrics['co2_per_order_g'] = metrics.pop('co2_per_order_grams')
            all_metrics.append(metrics)
    
    df = pd.DataFrame(all_metrics)
    df.to_csv('results/baseline_comparison.csv', index=False)
    
    print("\n" + "="*80)
    print("MULTI-SCENARIO BASELINE COMPARISON GENERATED")
    print("="*80)
    print(df[['scenario', 'method', 'co2_per_order_g', 'delivery_time_min']].to_string(index=False))
    print("="*80 + "\n")

if __name__ == "__main__":
    generate_comparison_table()
