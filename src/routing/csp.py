import networkx as nx
from src.routing.cost import edge_emission_cost

def find_route(graph: nx.DiGraph, origin: int, dest: int, vehicle_type: str, max_co2_budget_grams: float, time_of_day: str = 'peak'):
    """
    Constrained shortest path (CSP) using NetworkX.
    We optimize for time (or shortest path) while keeping emission under budget.
    """
    def weight_func(u, v, d):
        distance = d.get('length', 100.0)
        speed = d.get('speed_kph_peak' if time_of_day == 'peak' else 'speed_kph_offpeak', 20.0)
        return distance / (speed * 1000 / 3600)
        
    try:
        paths = nx.shortest_simple_paths(graph, origin, dest, weight=weight_func)
        
        for idx, path in enumerate(paths):
            if idx > 100:  # Bound the search
                break
                
            total_co2 = 0.0
            for i in range(len(path)-1):
                u, v = path[i], path[i+1]
                edge_data = graph[u][v]
                if isinstance(edge_data, dict) and 0 in edge_data:
                    edge_data = edge_data[0] # Handle MultiDiGraph
                total_co2 += edge_emission_cost(edge_data, vehicle_type, time_of_day)
                
            if total_co2 <= max_co2_budget_grams:
                return path
                
        return None # Infeasible
    except nx.NetworkXNoPath:
        return None
