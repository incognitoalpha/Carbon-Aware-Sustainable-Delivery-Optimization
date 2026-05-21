import os
import sys
import yaml
import numpy as np
import torch
import random
from pathlib import Path

# Add src to python path for testing
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.utils.seed import seed_everything

def test_directory_structure():
    expected_dirs = [
        "config",
        "data/raw",
        "data/processed",
        "data/synthetic",
        "src/emissions",
        "src/routing",
        "src/simulator",
        "src/rl",
        "src/baselines",
        "src/eval",
        "tests",
        "notebooks",
        ".github/workflows"
    ]
    for d in expected_dirs:
        assert os.path.isdir(d), f"Directory {d} does not exist"

def test_config_loads():
    with open("config/base.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    assert "seed" in config
    assert config["data"]["city"] == "mumbai"
    assert config["rl"]["algorithm"] == "ppo"

def test_seed_utility():
    seed_everything(42)
    val1 = random.random()
    np_val1 = np.random.rand()
    torch_val1 = torch.rand(1).item()
    
    seed_everything(42)
    val2 = random.random()
    np_val2 = np.random.rand()
    torch_val2 = torch.rand(1).item()
    
    assert val1 == val2
    assert np_val1 == np_val2
    assert torch_val1 == torch_val2
