def heuristic_batching(orders: list, max_batch_size: int = 3):
    """
    Greedy nearest-neighbour batching (no deadline awareness)
    """
    batched_orders = []
    unassigned = orders.copy()
    
    while unassigned:
        current_batch = [unassigned.pop(0)]
        
        while unassigned and len(current_batch) < max_batch_size:
            last_order = current_batch[-1]
            
            nearest = min(unassigned, key=lambda o: 
                ((o['pickup_lat'] - last_order['pickup_lat'])**2 + 
                 (o['pickup_lon'] - last_order['pickup_lon'])**2)
            )
            
            current_batch.append(nearest)
            unassigned.remove(nearest)
            
        batched_orders.append(current_batch)
        
    return batched_orders
