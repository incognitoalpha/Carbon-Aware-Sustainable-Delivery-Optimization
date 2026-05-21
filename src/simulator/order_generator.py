import pandas as pd
import numpy as np
import random
import os
import json
from datetime import datetime, timedelta

def generate_orders(seed=42, num_days=30, base_orders_per_day=1000):
    np.random.seed(seed)
    random.seed(seed)
    
    # Simulate Mumbai center area
    center_lat, center_lon = 18.9690, 72.8205
    hotspots = [(center_lat + np.random.normal(0, 0.02), center_lon + np.random.normal(0, 0.02)) for _ in range(5)]
    
    orders = []
    start_date = datetime(2026, 1, 1)
    order_id = 1
    
    for day in range(num_days):
        current_date = start_date + timedelta(days=day)
        # Poisson distribution for daily total
        daily_orders = np.random.poisson(base_orders_per_day)
        
        for _ in range(daily_orders):
            # Hour of day with peaks around 1pm and 8pm
            hour = int(np.random.choice([
                *range(11, 15), *range(18, 22), *range(8, 24)
            ]))
            minute = random.randint(0, 59)
            created_at = current_date + timedelta(hours=hour, minutes=minute)
            
            # SLA is typically 30-45 minutes
            deadline_at = created_at + timedelta(minutes=random.choice([30, 45]))
            
            # Pickup around hotspots (log-normal spread, though normal is simpler here)
            hotspot = random.choice(hotspots)
            # using normal approximation for simplicity in coordinates
            pickup_lat = hotspot[0] + np.random.normal(0, 0.005)
            pickup_lon = hotspot[1] + np.random.normal(0, 0.005)
            
            # Dropoff random in the city (larger spread)
            dropoff_lat = center_lat + np.random.normal(0, 0.02)
            dropoff_lon = center_lon + np.random.normal(0, 0.02)
            
            weight_kg = np.random.lognormal(mean=0.5, sigma=0.5)
            
            orders.append({
                'order_id': order_id,
                'pickup_lat': pickup_lat,
                'pickup_lon': pickup_lon,
                'dropoff_lat': dropoff_lat,
                'dropoff_lon': dropoff_lon,
                'created_at': created_at,
                'deadline_at': deadline_at,
                'weight_kg': round(weight_kg, 2)
            })
            order_id += 1
            
    df = pd.DataFrame(orders)
    os.makedirs('data/synthetic', exist_ok=True)
    df.to_parquet(f'data/synthetic/orders_{seed}.parquet', index=False)
    
    # Generate splits
    dates = [start_date + timedelta(days=i) for i in range(num_days)]
    train_end = int(num_days * 0.7)
    val_end = int(num_days * 0.85)
    
    train_dates = [d.strftime('%Y-%m-%d') for d in dates[:train_end]]
    val_dates = [d.strftime('%Y-%m-%d') for d in dates[train_end:val_end]]
    test_dates = [d.strftime('%Y-%m-%d') for d in dates[val_end:]]
    
    splits = {
        'train': train_dates,
        'val': val_dates,
        'test': test_dates
    }
    
    os.makedirs('data/processed', exist_ok=True)
    with open('data/processed/splits.json', 'w') as f:
        json.dump(splits, f, indent=2)

if __name__ == "__main__":
    generate_orders()
