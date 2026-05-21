class InfeasibleRouteError(Exception):
    pass

def ev_co2_grams(distance_km: float, soc_pct: float, temp_celsius: float, 
                 kwh_per_km: float = 0.025, battery_kwh: float = 3.0,
                 ev_reserve_soc: float = 0.15, is_steep: bool = False,
                 grid_intensity: float = 708.0) -> float:
    
    temp_penalty = 0.0
    if temp_celsius < 20:
        temp_penalty = (20 - temp_celsius) * 0.01
    elif temp_celsius > 35:
        temp_penalty = (temp_celsius - 35) * 0.005
        
    peukert_factor = 1.1 if is_steep else 1.0
    
    effective_kwh_per_km = kwh_per_km / (1.0 - temp_penalty) * peukert_factor
    energy_used_kwh = distance_km * effective_kwh_per_km
    
    soc_drop_pct = energy_used_kwh / battery_kwh
    projected_soc = soc_pct - soc_drop_pct
    
    if projected_soc < ev_reserve_soc:
        raise InfeasibleRouteError(f"Projected SoC {projected_soc:.2f} falls below reserve {ev_reserve_soc:.2f}.")
        
    return energy_used_kwh * grid_intensity
