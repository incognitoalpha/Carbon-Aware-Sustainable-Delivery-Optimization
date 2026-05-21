import pytest
import os
import sys
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.eval.metrics import compute_metrics
from src.eval.pareto import ParetoTracker

def test_compute_metrics():
    # Mock data
    results = pd.DataFrame([
        {'co2_per_order_g': 100.0, 'delivery_time_min': 20.0, 'is_sla_breach': False},
        {'co2_per_order_g': 80.0, 'delivery_time_min': 35.0, 'is_sla_breach': True}
    ])
    
    baseline = pd.DataFrame([
        {'co2_per_order_g': 120.0, 'delivery_time_min': 15.0, 'is_sla_breach': False},
        {'co2_per_order_g': 120.0, 'delivery_time_min': 15.0, 'is_sla_breach': False}
    ])
    
    metrics = compute_metrics(results, baseline)
    assert not pd.isna(metrics['co2_per_order_grams'])
    assert metrics['co2_per_order_grams'] == 90.0
    assert metrics['sla_compliance_pct'] == 50.0
    assert metrics['rider_earnings_index'] > 0
    assert metrics['operational_cost_index'] > 0

def test_pareto_report(tmp_path):
    tracker = ParetoTracker(log_dir=str(tmp_path))
    tracker.log_epoch(1, 20.0, 90.0)
    tracker.log_epoch(2, 18.0, 85.0)
    tracker.log_epoch(3, 15.0, 100.0) 
    
    tracker.plot_pareto()
    tracker.generate_report()
    
    report_path = os.path.join(tmp_path, 'pareto_report.md')
    assert os.path.exists(report_path)
    with open(report_path, 'r') as f:
        content = f.read()
        assert "Pareto Evaluation Report" in content
        assert "18.0" in content

def test_dashboard_exists():
    assert os.path.exists("src/eval/dashboard.html")

def test_github_actions_yaml_validity():
    import yaml
    assert os.path.exists(".github/workflows/eval.yml")
    with open(".github/workflows/eval.yml", "r") as f:
        workflow = yaml.safe_load(f)
    assert 'jobs' in workflow
