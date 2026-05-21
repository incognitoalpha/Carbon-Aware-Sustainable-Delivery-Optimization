import numpy as np

def get_randomized_parameters(seed=None):
    if seed is not None:
        np.random.seed(seed)
        
    travel_time_noise = np.random.uniform(0.85, 1.15)
    demand_scale = np.random.uniform(0.7, 1.3)
    emission_factor_noise = np.random.uniform(0.80, 1.20)
    
    return {
        'travel_time_noise': travel_time_noise,
        'demand_scale': demand_scale,
        'emission_factor_noise': emission_factor_noise
    }
