import pandas as pd
import matplotlib.pyplot as plt
import os

class ParetoTracker:
    def __init__(self, log_dir='results'):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.csv_path = os.path.join(self.log_dir, 'pareto_front.csv')
        self.history = []
        
    def log_epoch(self, epoch: int, mean_delivery_time: float, mean_co2_per_order: float):
        self.history.append({
            'epoch': epoch,
            'mean_delivery_time': mean_delivery_time,
            'mean_co2_per_order': mean_co2_per_order
        })
        df = pd.DataFrame(self.history)
        df.to_csv(self.csv_path, index=False)
        
    def plot_pareto(self):
        if not self.history:
            return
        df = pd.DataFrame(self.history)
        
        plt.figure(figsize=(8, 6))
        plt.scatter(df['mean_co2_per_order'], df['mean_delivery_time'])
        plt.xlabel("Mean CO2 per Order (grams)")
        plt.ylabel("Mean Delivery Time (min)")
        plt.title("Pareto Front")
        plt.savefig(os.path.join(self.log_dir, 'pareto_front.png'))
        plt.close()
        
    def generate_report(self):
        if not self.history:
            return
            
        df = pd.DataFrame(self.history)
        
        feasible = df[df['mean_delivery_time'] <= 30.6] 
        if len(feasible) > 0:
            best_point = feasible.loc[feasible['mean_co2_per_order'].idxmin()]
        else:
            best_point = df.loc[df['mean_co2_per_order'].idxmin()]
            
        report = f"""# Pareto Evaluation Report

![Pareto Front](pareto_front.png)

## Pareto-Optimal Configurations
{df.to_markdown(index=False)}

## Highlighted Best Point
- **Epoch:** {int(best_point['epoch'])}
- **Mean Delivery Time:** {best_point['mean_delivery_time']:.2f} min
- **Mean CO2 per Order:** {best_point['mean_co2_per_order']:.2f} grams
"""
        with open(os.path.join(self.log_dir, 'pareto_report.md'), 'w') as f:
            f.write(report)
