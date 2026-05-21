# Base factors for petrol_bike in g/km
HBEFA_LITE = {
    'petrol_bike': {
        '0-10': 110.0,
        '10-30': 89.0,
        '30-50': 75.0,
        '50+': 95.0
    },
    'ev_bike': {
        '0-10': 0.0,
        '10-30': 0.0,
        '30-50': 0.0,
        '50+': 0.0
    },
    'bicycle': {
        '0-10': 0.0,
        '10-30': 0.0,
        '30-50': 0.0,
        '50+': 0.0
    }
}

def get_speed_band(speed_kph: float) -> str:
    if speed_kph < 10:
        return '0-10'
    elif speed_kph < 30:
        return '10-30'
    elif speed_kph < 50:
        return '30-50'
    else:
        return '50+'

def get_emission_factor(vehicle_type: str, speed_kph: float) -> float:
    band = get_speed_band(speed_kph)
    return HBEFA_LITE.get(vehicle_type, {}).get(band, 0.0)
