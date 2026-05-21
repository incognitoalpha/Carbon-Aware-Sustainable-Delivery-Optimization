import pandas as pd
import numpy as np
from datetime import datetime
import os

class WeatherStub:
    def __init__(self, csv_path='data/raw/weather_stub.csv'):
        if not os.path.exists(csv_path):
            self._generate_stub(csv_path)
        self.df = pd.read_csv(csv_path, parse_dates=['timestamp'])
        self.df.set_index('timestamp', inplace=True)
        
    def _generate_stub(self, path):
        # Generate 30 days of stub data
        os.makedirs(os.path.dirname(path), exist_ok=True)
        dates = pd.date_range('2026-01-01', periods=30*24, freq='h')
        
        # Base temp 25C, diurnal variation +/- 5C
        temps = 25 + 5 * np.sin((dates.hour - 6) * np.pi / 12)
        precip = np.random.choice([0, 1], size=len(dates), p=[0.9, 0.1])
        
        df = pd.DataFrame({
            'timestamp': dates,
            'temperature_c': temps,
            'precipitation_flag': precip
        })
        df.to_csv(path, index=False)
        
    def get_weather(self, dt: datetime):
        """Returns (temperature_c, precipitation_flag) for a given datetime."""
        # Find nearest hour
        nearest_hour = dt.replace(minute=0, second=0, microsecond=0)
        if dt.minute >= 30:
            from datetime import timedelta
            nearest_hour += timedelta(hours=1)
            
        try:
            row = self.df.loc[nearest_hour]
            return row['temperature_c'], row['precipitation_flag']
        except KeyError:
            return 25.0, 0 # Default fallback
