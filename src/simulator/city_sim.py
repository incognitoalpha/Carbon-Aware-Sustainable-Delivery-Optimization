import simpy
import random
from typing import List, Dict
from datetime import datetime, timedelta

class CitySimulator(simpy.Environment):
    def __init__(self, config: dict, orders: List[Dict], fleet: List[Dict]):
        super().__init__()
        self.config = config
        self.orders = orders
        self.fleet = fleet
        
        self.unassigned_orders = list(orders)
        self.delivered_orders = []
        self.sla_breaches = 0
        self.ev_battery_violations = 0
        self.metrics = []
        
        self.dispatch_interval = 0.5 
        self.start_time = datetime(2026, 1, 1, 8, 0) # 8 AM start
        
        self.process(self.dispatch_loop())
        
    def dispatch_loop(self):
        while self.now < 86400 / 60.0:
            if not self.unassigned_orders:
                break
                
            batch = self.unassigned_orders[:5]
            for order in batch:
                self.unassigned_orders.remove(order)
                
                # Simulate picking a vehicle from the fleet
                vehicle = random.choice(self.fleet)
                v_type = vehicle.get('type', 'petrol_bike')
                
                # Simulate realistic delivery time and CO2 based on vehicle type
                if v_type == 'bicycle':
                    delivery_time = random.uniform(25.0, 45.0)
                    co2 = 0.0
                    final_soc = 1.0 # Bicycles don't have SoC in this model
                elif v_type == 'ev_bike':
                    delivery_time = random.uniform(15.0, 30.0)
                    co2 = random.uniform(5.0, 15.0) # Indirect emissions
                    final_soc = max(0.0, random.uniform(0.6, 0.95))
                else: # petrol_bike
                    delivery_time = random.uniform(12.0, 25.0)
                    co2 = random.uniform(80.0, 150.0)
                    final_soc = 1.0
                
                if delivery_time > 30.0:
                    self.sla_breaches += 1
                
                # Check SoC constraint
                if v_type == 'ev_bike' and final_soc < self.config.get('ev_reserve_soc', 0.15):
                    self.ev_battery_violations += 1
                
                current_dt = self.start_time + timedelta(minutes=self.now)
                
                self.delivered_orders.append(order)
                self.metrics.append({
                    'order_id': order.get('order_id', 0),
                    'delivery_time_min': delivery_time,
                    'co2_per_order_g': co2,
                    'is_sla_breach': delivery_time > 30.0,
                    'vehicle_type': v_type,
                    'final_soc': final_soc,
                    'hour_of_day': current_dt.hour
                })
                
            yield self.timeout(self.dispatch_interval)
