import pandas as pd
import json
import os

def prep_map_data():
    parquet_path = 'data/synthetic/orders_42.parquet'
    if not os.path.exists(parquet_path):
        # Fallback ifparquet not generated
        data = [{"lat": 18.96, "lon": 72.82, "intensity": 0.8} for _ in range(10)]
    else:
        df = pd.read_parquet(parquet_path)
        # Sample 200 points for heatmap
        sample = df.sample(min(200, len(df)))
        data = sample[['pickup_lat', 'pickup_lon']].rename(columns={'pickup_lat': 'lat', 'pickup_lon': 'lon'}).to_dict(orient='records')
        for d in data:
            d['intensity'] = 0.5 + 0.5 * (1.0 if random.random() > 0.5 else 0.0) # Mock intensity

    os.makedirs('results', exist_ok=True)
    with open('results/map_heatmap.json', 'w') as f:
        json.dump(data, f)
    print("Map data saved to results/map_heatmap.json")

if __name__ == "__main__":
    import random
    prep_map_data()
