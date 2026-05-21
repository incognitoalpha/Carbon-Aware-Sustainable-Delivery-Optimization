from .hbefa import get_emission_factor

def idle_co2_grams(vehicle_type: str, idle_seconds: float) -> float:
    if idle_seconds <= 30:
        return 0.0
    
    idle_factor_gs = 0.0
    if vehicle_type == 'petrol_bike':
        idle_factor_gs = 0.025
        
    return idle_factor_gs * idle_seconds
