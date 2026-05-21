import pytest
import os
import sys
from pathlib import Path
from gymnasium.utils.env_checker import check_env

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rl.env import CarbonDeliveryEnv
from src.rl.domain_rand import get_randomized_parameters
from src.eval.pareto import ParetoTracker

def test_environment():
    env = CarbonDeliveryEnv()
    check_env(env)
    
    obs, info = env.reset()
    assert obs.shape == (6,)
    
    obs, reward, terminated, truncated, info = env.step(0)
    assert not terminated
    
    assert env.lagrangian_multiplier >= 0.0
    
    env.co2_budget_per_order = 0.0
    obs, reward, terminated, truncated, info = env.step(0)
    assert env.lagrangian_multiplier > 0.0

def test_domain_randomization():
    params1 = get_randomized_parameters(seed=42)
    params2 = get_randomized_parameters(seed=42)
    
    assert params1['travel_time_noise'] == params2['travel_time_noise']
    assert 0.85 <= params1['travel_time_noise'] <= 1.15
    assert 0.7 <= params1['demand_scale'] <= 1.3
    assert 0.80 <= params1['emission_factor_noise'] <= 1.20

def test_pareto_tracker(tmp_path):
    tracker = ParetoTracker(log_dir=str(tmp_path))
    tracker.log_epoch(1, 20.0, 90.0)
    tracker.log_epoch(2, 18.0, 85.0)
    
    assert os.path.exists(os.path.join(tmp_path, 'pareto_front.csv'))
    tracker.plot_pareto()
    assert os.path.exists(os.path.join(tmp_path, 'pareto_front.png'))
