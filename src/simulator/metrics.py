import pandas as pd
import os

def log_metrics(metrics: list, scenario: str, policy: str, seed: int):
    os.makedirs('results', exist_ok=True)
    df = pd.DataFrame(metrics)
    
    file_path = f"results/sim_{scenario}_{policy}_{seed}.parquet"
    df.to_parquet(file_path, index=False)
