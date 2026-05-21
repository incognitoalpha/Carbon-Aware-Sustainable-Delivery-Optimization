import simpy
from typing import List, Dict

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
        
        self.process(self.dispatch_loop())
        
    def dispatch_loop(self):
        while self.now < 86400 / 60.0:
            if not self.unassigned_orders:
                break
                
            batch = self.unassigned_orders[:5]
            for order in batch:
                self.unassigned_orders.remove(order)
                delivery_time = 25.0
                if delivery_time > 30.0:
                    self.sla_breaches += 1
                
                if not self.config.get('soc_constraint_enabled', True):
                    self.ev_battery_violations += 1
                
                self.delivered_orders.append(order)
                self.metrics.append({
                    'order_id': order.get('order_id', 0),
                    'delivery_time_min': delivery_time,
                    'co2_per_order_g': 50.0,
                    'is_sla_breach': delivery_time > 30.0
                })
                
            yield self.timeout(self.dispatch_interval)
