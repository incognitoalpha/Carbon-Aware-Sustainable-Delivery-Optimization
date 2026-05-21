from src.emissions.hbefa import get_emission_factor
from src.emissions.ev import ev_co2_grams

def edge_emission_cost(edge_data: dict, vehicle_type: str, time_of_day: str) -> float:
    distance_km = edge_data.get('length', 100.0) / 1000.0
    
    speed_kph = edge_data.get('speed_kph_peak', 20.0)
    if time_of_day == 'offpeak':
        speed_kph = edge_data.get('speed_kph_offpeak', 30.0)
        
    if vehicle_type == 'ev_bike':
        return ev_co2_grams(distance_km, 0.5, 25.0)
    else:
        factor = get_emission_factor(vehicle_type, speed_kph)
        return distance_km * factor

def composite_cost(edge_data: dict, vehicle_type: str, time_of_day: str, 
                   alpha_time: float, alpha_emission: float) -> float:
    emission_g = edge_emission_cost(edge_data, vehicle_type, time_of_day)
    
    distance_m = edge_data.get('length', 100.0)
    speed_kph = edge_data.get('speed_kph_peak' if time_of_day == 'peak' else 'speed_kph_offpeak', 20.0)
    time_s = distance_m / (speed_kph * 1000 / 3600)
    
    return alpha_time * time_s + alpha_emission * emission_g
