# Carbon-Aware Sustainable Delivery Optimization

## Overview
This project simulates and optimizes city-scale delivery routing by balancing SLA compliance with carbon emissions. It employs a Lagrangian-constrained reinforcement learning (PPO) agent against an emission-aware shortest path baseline, aiming for a Pareto-optimal delivery model that accounts for hyperlocal EV state-of-charge constraints and real-time traffic emission overlays.

## Architecture
- **Data Pipeline:** Pulls OSM road networks and overlays BRouter time-of-day speed profiles. Generates synthetic city-scale orders.
- **Emissions Estimator:** Uses HBEFA 4.2 lite parameters with idle/temperature penalties.
- **Routing Engine:** Integrates OSRM and dynamic emission-weighted edge costs to evaluate optimal paths constraint by maximum emission budgets.
- **RL Optimization:** A Custom SimPy + Gymnasium environment optimizing routing via PPO while treating SLA and carbon budget as Lagrangian constraints.
- **Simulator & Evaluation:** SimPy discrete-event simulation tracking metrics along a Pareto front comparing RL routing vs fastest-route baselines.

## Quickstart
```bash
# Clone the repository and install dependencies
git clone <repo> && cd carbon-delivery-opt
pip install -r requirements.txt

# Run the training pipeline and evaluate baseline comparisons
python src/rl/train.py --config-name=base seed=42
python src/eval/compare.py --config-name=base seed=42
```

## Limitations
- Static OSM graph (no real-time closures)
- BRouter speed profiles (±15% vs GPS ground truth)
- Peukert EV model without elevation (±10% range estimate)
- Grid emission factor: India 2023 (update annually)
- Sim-to-real gap: domain randomization applied, not validated on live fleet

## Citing
If you use this work, please consider the novel combination of constrained RL, hyperlocal EV SoC constraints, and real-time traffic emission overlays applied to last-mile logistics routing.
