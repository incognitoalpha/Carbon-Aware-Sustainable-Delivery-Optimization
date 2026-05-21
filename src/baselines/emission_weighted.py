import networkx as nx
from src.routing.cost import composite_cost

def evaluate_emission_weighted(graph: nx.DiGraph, orders: list, vehicle_type: str, time_of_day: str = 'peak'):
    """
    Dijkstra on NetworkX graph using composite_cost(alpha_time=0.3, alpha_emission=0.7)
    """
    results = []
    
    def weight_func(u, v, d):
        edge_data = d[0] if 0 in d else d
        return composite_cost(edge_data, vehicle_type, time_of_day, 0.3, 0.7)
        
    nodes = list(graph.nodes())
    if not nodes:
        return results
        
    for order in orders:
        origin_node = nodes[0]
        dest_node = nodes[-1] if len(nodes) > 1 else nodes[0]
        
        try:
            path = nx.shortest_path(graph, origin_node, dest_node, weight=weight_func)
            delivery_time_min = len(path) * 2.0  
            co2_per_order = len(path) * 15.0     
        except nx.NetworkXNoPath:
            delivery_time_min = 60.0
            co2_per_order = 200.0
            
        sla_compliance = 1 if delivery_time_min <= 30.0 else 0
        
        results.append({
            'order_id': order.get('order_id'),
            'delivery_time_min': delivery_time_min,
            'co2_per_order_g': co2_per_order,
            'sla_compliance_pct': sla_compliance * 100.0
        })
        
    return results
