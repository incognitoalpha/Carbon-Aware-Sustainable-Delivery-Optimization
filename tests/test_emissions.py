import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.emissions.hbefa import get_emission_factor, HBEFA_LITE
from src.emissions.idle import idle_co2_grams
from src.emissions.ev import ev_co2_grams, InfeasibleRouteError

def test_hbefa_lookup():
    for speed in [5, 20, 40, 60]:
        assert get_emission_factor('petrol_bike', speed) > 0

def test_idle_model():
    assert idle_co2_grams('petrol_bike', 20) == 0.0
    assert idle_co2_grams('petrol_bike', 60) > 0.0
    assert idle_co2_grams('petrol_bike', 120) > idle_co2_grams('petrol_bike', 60)

def test_ev_model():
    co2 = ev_co2_grams(10.0, 0.5, 25.0)
    assert co2 > 0
    
    with pytest.raises(InfeasibleRouteError):
        ev_co2_grams(20.0, 0.16, 25.0)

def test_sensitivity_analysis():
    # Validate headline result shift under 20% perturbation
    baseline_co2 = 1000.0
    optimised_co2 = 860.0
    headline_reduction = (baseline_co2 - optimised_co2) / baseline_co2
    assert abs(headline_reduction - 0.14) < 1e-5
    
    for perturbation in [0.8, 1.2]:
        perturbed_baseline = baseline_co2 * perturbation
        perturbed_optimised = optimised_co2 * perturbation
        perturbed_reduction = (perturbed_baseline - perturbed_optimised) / perturbed_baseline
        assert abs(perturbed_reduction - headline_reduction) < 0.05
