from datetime import datetime

class EVSoCConstraintError(Exception):
    pass

def can_batch(order_A: dict, order_B: dict, rider_soc: float = None, 
              batch_window_minutes: int = 10, max_detour_ratio: float = 1.3,
              ev_reserve_soc: float = 0.15, route_energy_cost: float = 0.0) -> bool:
    
    deadline_diff = abs((order_A['deadline_at'] - order_B['deadline_at']).total_seconds()) / 60.0
    if deadline_diff >= batch_window_minutes:
        return False
        
    if rider_soc is not None:
        if rider_soc - route_energy_cost < ev_reserve_soc:
            return False
            
    dist_pickups = ((order_A['pickup_lat'] - order_B['pickup_lat'])**2 + 
                    (order_A['pickup_lon'] - order_B['pickup_lon'])**2)**0.5
    dist_m = dist_pickups * 111000
    
    if dist_m > 5000:
        return False
        
    return True

def prioritize_orders(orders: list, available_riders: int):
    # Surge: prioritize by deadline, not proximity
    if len(orders) > available_riders:
        return sorted(orders, key=lambda x: x['deadline_at'])
    return orders
