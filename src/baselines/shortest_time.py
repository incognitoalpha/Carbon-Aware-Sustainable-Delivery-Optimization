from src.routing.osrm_client import OSRMClient

def evaluate_shortest_time(orders: list, vehicle_profile: str = "bike"):
    """
    Pure OSRM fastest route, no emission awareness.
    Returns list of metrics per order.
    """
    client = OSRMClient()
    results = []
    
    for order in orders:
        origin = (order['pickup_lat'], order['pickup_lon'])
        dest = (order['dropoff_lat'], order['dropoff_lon'])
        
        route = client.get_route(origin, dest, vehicle_profile)
        
        delivery_time_min = route['duration_s'] / 60.0
        co2_per_order = route['distance_m'] / 1000.0 * 89.0 # approx for petrol_bike
        
        sla_compliance = 1 if delivery_time_min <= 30.0 else 0
        
        results.append({
            'order_id': order.get('order_id'),
            'delivery_time_min': delivery_time_min,
            'co2_per_order_g': co2_per_order,
            'sla_compliance_pct': sla_compliance * 100.0
        })
        
    return results
