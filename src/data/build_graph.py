import osmnx as ox
import networkx as nx
import random
import os

def build_graph():
    """
    Downloads OSM graph and overlays city-class average speed profiles.
    > ⚠️ ASSUMPTION: Speed profiles are city-class averages, not GPS-trace-calibrated. 
    > Error bound: ±15% vs ground truth per BRouter paper.
    """
    # 2.1 OSM graph download
    print("Downloading OSM graph for Mumbai (10x10km)...")
    # Coordinates for Mumbai central, approx 5km radius = 10km diameter
    G = ox.graph_from_point((18.9690, 72.8205), dist=5000, network_type='drive')
    
    os.makedirs("data/raw", exist_ok=True)
    ox.save_graphml(G, "data/raw/osm_graph.graphml")
    print("Saved to data/raw/osm_graph.graphml")

    # 2.2 Speed profile overlay
    print("Overlaying speed profiles...")
    for u, v, k, data in G.edges(keys=True, data=True):
        hw = data.get('highway', 'residential')
        if isinstance(hw, list):
            hw = hw[0]
            
        # Base speed by highway type
        if hw in ['primary', 'primary_link', 'trunk', 'trunk_link']:
            base_speed = 50.0
        elif hw in ['secondary', 'secondary_link']:
            base_speed = 40.0
        elif hw in ['tertiary', 'tertiary_link']:
            base_speed = 30.0
        else:
            base_speed = 20.0
            
        data['speed_kph_peak'] = base_speed * 0.6  # 40% reduction during peak
        data['speed_kph_offpeak'] = base_speed * 0.9 # 10% reduction during offpeak

    os.makedirs("data/processed", exist_ok=True)
    ox.save_graphml(G, "data/processed/graph_with_speeds.graphml")
    print("Saved to data/processed/graph_with_speeds.graphml")

if __name__ == "__main__":
    build_graph()
