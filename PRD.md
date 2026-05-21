# PRD — Carbon-Aware Sustainable Delivery Optimization
> **Agent directive:** This document is your single source of truth. Work through every checkbox in order. After completing each major task, run the specified test suite before checking the box and moving on. For every task, consult the listed skill(s) first — do not proceed without reading them. Cross off each checkbox by replacing `[ ]` with `[x]` in this file as you complete it.

---

## 0. Agent Rules (read before anything else)

- **Never skip a skill reference.** Each task lists required skills. Read the SKILL.md before writing a single line of code or prose.
- **Never mark a checkbox complete without passing tests.** If tests fail, fix and re-run before proceeding.
- **Document every assumption.** If a data source, formula, or design choice is an approximation, add a `> ⚠️ ASSUMPTION:` block inline in the relevant source file.
- **Reproducibility is non-negotiable.** Every run must be reproducible from a single command. Seed all randomness. Pin all dependencies.
- **Commit after every major task.** Commit message format: `[TASK-N] short description — tests: pass`.

---

## 1. Repository & Project Scaffold

**Skills required:**
- `file-reading` — `/mnt/skills/public/file-reading/SKILL.md` (for reading any uploaded config/data files during setup)
- `doc-coauthoring` — `/mnt/skills/examples/doc-coauthoring/SKILL.md` (for README and documentation structure)

### Tasks

- [x] **1.1** Initialise git repo with the following top-level structure:
  ```
  carbon-delivery-opt/
  ├── config/           # Hydra YAML configs (one per experiment)
  ├── data/
  │   ├── raw/          # OSM exports, GPS traces, weather CSVs
  │   ├── processed/    # Cleaned, versioned splits
  │   └── synthetic/    # Generated order datasets
  ├── src/
  │   ├── emissions/    # Emission factor models
  │   ├── routing/      # Graph engine wrapper
  │   ├── simulator/    # City-scale SimPy environment
  │   ├── rl/           # Agent, reward, training loop
  │   ├── baselines/    # All comparison algorithms
  │   └── eval/         # Metrics, Pareto front, plots
  ├── tests/            # Mirrors src/ structure
  ├── notebooks/        # EDA, sensitivity analysis
  ├── .github/workflows/eval.yml
  ├── requirements.txt  # All deps pinned to exact versions
  ├── README.md
  └── PRD.md            # This file — keep updated
  ```

- [x] **1.2** Create `requirements.txt` pinning:
  `osmnx`, `networkx`, `simpy`, `gymnasium`, `stable-baselines3`, `torch`, `hydra-core`, `omegaconf`, `pandas`, `numpy`, `matplotlib`, `pytest`, `pytest-cov`, `dvc` (for data versioning).

- [x] **1.3** Write `config/base.yaml` with all global seeds, paths, and hyperparameter defaults. Every subsequent config inherits from this via Hydra `defaults:`.
  ```yaml
  seed: 42
  data:
    city: "mumbai"
    grid_km: 10
    orders_per_day: 10000
  emissions:
    factor_source: "hbefa_lite"
    ev_reserve_soc: 0.15
  rl:
    algorithm: "ppo"
    constraint_method: "lagrangian"
  ```

- [x] **1.4** Pin random seeds in a `src/utils/seed.py` utility. Call it at the top of every script and training entry point.

- [x] **1.5** Write `README.md` using the doc-coauthoring structure: overview → architecture → quickstart (one command to reproduce headline result) → limitations → citing.

**Tests for Task 1:**
- [x] `pytest tests/test_scaffold.py` — verify directory structure exists, config loads without error, seed utility sets identical state across two runs.

---

## 2. Data Pipeline

**Skills required:**
- `file-reading` — `/mnt/skills/public/file-reading/SKILL.md` (reading OSM exports, CSVs, GPS traces)
- `xlsx` — `/mnt/skills/public/xlsx/SKILL.md` (if any input data arrives as spreadsheets from Uber Movement or HBEFA)

### Tasks

- [x] **2.1 OSM graph download**
  Use `osmnx.graph_from_place()` for a 10×10 km urban bounding box (default: Mumbai central). Save as `data/raw/osm_graph.graphml`. Add a DVC `.dvc` file to version it.

  > ⚠️ ASSUMPTION: Static OSM graph used as road network backbone. Dynamic closures not modelled in v1.

- [x] **2.2 Speed profile overlay**
  Download BRouter time-of-day speed profiles (free, open-source). Merge onto OSM edge attributes as `speed_kph_peak` and `speed_kph_offpeak`. Save to `data/processed/graph_with_speeds.graphml`.

  > ⚠️ ASSUMPTION: Speed profiles are city-class averages, not GPS-trace-calibrated. Document error bound: ±15% vs ground truth per BRouter paper (cite in README).

- [x] **2.3 Synthetic order generator**
  Write `src/simulator/order_generator.py`:
  - Poisson-distributed arrival rate, configurable per hour
  - Spatial distribution: log-normal cluster around restaurant hotspots (seed-controlled)
  - Outputs: `data/synthetic/orders_{seed}.parquet` with columns: `order_id, pickup_lat, pickup_lon, dropoff_lat, dropoff_lon, created_at, deadline_at, weight_kg`
  - Fixed train/val/test split: 70/15/15 by date, committed to repo as `data/processed/splits.json`

- [x] **2.4 Rider fleet definition**
  Write `data/processed/fleet.json` defining vehicle types:
  ```json
  [
    {"type": "petrol_bike", "co2_per_km_grams": 89, "speed_factor": 1.0},
    {"type": "ev_bike",     "co2_per_km_grams": 0,  "kwh_per_km": 0.025, "battery_kwh": 3.0, "speed_factor": 0.95},
    {"type": "bicycle",     "co2_per_km_grams": 0,  "speed_factor": 0.6}
  ]
  ```
  Source emission factors from **HBEFA 4.2 lite** (public research tables, cite DOI in README).

- [x] **2.5 Weather data stub**
  Write `src/data/weather.py` that returns temperature (°C) and precipitation flag per timestamp from a CSV. Use ERA5 reanalysis data (free via CDS API, or commit a 30-day sample CSV). Wire temperature into EV range degradation in Task 3.

**Tests for Task 2:**
- [x] `pytest tests/test_data_pipeline.py` — verify:
  - OSM graph has ≥ 1000 nodes
  - Speed attributes present on all edges
  - Order generator produces deterministic output given same seed
  - Fleet JSON passes schema validation
  - Train/val/test splits are non-overlapping

---

## 3. Emissions Estimator

> **Critical fix addressed here:** *Emissions model was fake precision.* This task implements a peer-referenced, sensitivity-tested model.

**Skills required:**
- `file-reading` — `/mnt/skills/public/file-reading/SKILL.md` (reading HBEFA factor tables)

### Tasks

- [x] **3.1 HBEFA emission factor loader**
  Write `src/emissions/hbefa.py`:
  - Load lookup table: `{vehicle_class, speed_band_kph} → g_CO2_per_km`
  - Speed bands: `[0–10, 10–30, 30–50, 50+]` kph (idle, urban-slow, urban-fast, arterial)
  - Source: HBEFA 4.2 lite tables (public research document — extract values, cite in docstring)

- [x] **3.2 Idle emission model**
  Write `src/emissions/idle.py`:
  - `idle_co2_grams(vehicle_type, idle_seconds)` using HBEFA idle factors
  - Applied whenever a rider is stationary for > 30s (traffic signal, pickup wait)

- [x] **3.3 EV energy + indirect emissions model**
  Write `src/emissions/ev.py`:
  - `ev_co2_grams(distance_km, soc_pct, temp_celsius)` using:
    - Base: `kwh_per_km` from fleet config
    - Temperature penalty: −1% range per °C below 20°C, −0.5% per °C above 35°C (cite Yuksel & Michalek 2015)
    - Peukert adjustment factor for high-load segments (factor = 1.1 on steep grades if elevation data available, else 1.0)
    - Grid emission factor: India CEA 2023 grid intensity = **708 g CO₂/kWh** (cite CEA annual report, update yearly)
  - Hard constraint: `raise InfeasibleRouteError` if projected SoC at destination < `ev_reserve_soc` (15% from config)

- [x] **3.4 Sensitivity analysis notebook**
  Write `notebooks/sensitivity_analysis.ipynb`:
  - Vary each emission factor by ±20%
  - Show that headline CO₂ reduction result changes by < 5 percentage points
  - **This notebook must be committed with all outputs pre-run** (reviewers should not need to re-execute)

  > **This directly defends the resume claim.** If the 14% number shifts to 8% or 22% under sensitivity, revise the claim or the model — do not publish a fragile number.

**Tests for Task 3:**
- [x] `pytest tests/test_emissions.py` — verify:
  - HBEFA lookup returns non-zero for all vehicle/speed combinations
  - EV model raises `InfeasibleRouteError` when SoC would drop below 15%
  - Idle model produces monotonically increasing grams with idle time
  - Sensitivity analysis: headline result within ±5pp across all ±20% factor perturbations

---

## 4. Graph Routing Engine

> **Critical fix addressed here:** *Naive Dijkstra won't scale.* This task wraps OSRM with custom cost functions.

**Skills required:**
- `file-reading` — `/mnt/skills/public/file-reading/SKILL.md` (reading OSRM config files if customising profiles)

### Tasks

- [x] **4.1 OSRM wrapper**
  Write `src/routing/osrm_client.py`:
  - Wrap OSRM HTTP API (self-hosted via Docker, free)
  - Methods: `get_route(origin, destination, vehicle_profile)` → `{distance_m, duration_s, polyline}`
  - Default profiles: `bike`, `foot` (OSRM built-in). Document how to add EV profile.
  - Include Docker Compose file in repo: `docker/docker-compose.yml` to spin up OSRM with OSM data.

  > ⚠️ ASSUMPTION: OSRM used for geometry and time; emission cost computed as post-processing overlay on returned route. Contraction hierarchies handle scale; no custom routing graph built from scratch.

- [x] **4.2 Emission-weighted edge cost**
  Write `src/routing/cost.py`:
  - `edge_emission_cost(edge, vehicle_type, time_of_day)` using Task 3 estimator + Task 2 speed profiles
  - `composite_cost(edge, alpha_time, alpha_emission)` — weighted sum, weights from config
  - Used by baselines (Task 6) and RL reward (Task 5)

- [x] **4.3 Constrained shortest path baseline**
  Write `src/routing/csp.py`:
  - NetworkX-based Dijkstra with emission budget as a hard constraint
  - `find_route(graph, origin, dest, vehicle_type, max_co2_budget_grams)` → route or `None`
  - This is the strongest heuristic baseline — RL must beat this, not just Google Maps ETA

- [x] **4.4 Batching engine**
  Write `src/routing/batching.py`:
  - Time-constrained bin packing: batch orders only if `|deadline_A - deadline_B| < batch_window_minutes` (default: 10 min, configurable)
  - Spatial gate: only batch if detour ratio < 1.3× direct route
  - Edge cases that MUST be handled (and tested):
    - Two orders 200m apart, 30 min deadline apart → **do not batch**
    - EV at 20% SoC offered a long batch → **reject via SoC constraint**
    - Surge: 50 orders, 3 riders → **prioritise by deadline, not proximity**

**Tests for Task 4:**
- [x] `pytest tests/test_routing.py` — verify:
  - OSRM returns valid route for known origin/destination pair
  - Emission-weighted cost is strictly higher on high-traffic edges at peak hours
  - CSP returns `None` when budget is infeasible, valid route otherwise
  - All three batching edge cases return the documented expected behaviour

---

## 5. RL Optimization Service

> **Critical fix addressed here:** *Multi-objective reward collapse.* This task implements Lagrangian-constrained RL, not naively weighted scalarization.

**Skills required:**
- None from skills list beyond general coding standards — use PyTorch + Stable-Baselines3 + Gymnasium.

### Tasks

- [x] **5.1 Gymnasium environment**
  Write `src/rl/env.py` — `CarbonDeliveryEnv(gym.Env)`:
  - **State space:** `[order_pickup_dist, order_deadline_remaining, rider_soc, rider_vehicle_type, traffic_intensity, weather_temp]`
  - **Action space:** `Discrete(N_actions)` — N pre-computed route options per dispatch decision
  - **Reward:** `R = -delivery_time_minutes` (only time — the objective we maximise)
  - **Constraint:** `C = grams_CO2_per_order ≤ CO2_budget_per_order` (from config, default: 20% below fleet average)
  - **Method:** Lagrangian relaxation — add `λ * max(0, C - CO2_budget)` penalty term; λ is a learned multiplier updated each episode
  - `render()` method: print episode stats as a table

- [x] **5.2 Training script**
  Write `src/rl/train.py`:
  - Algorithm: PPO via Stable-Baselines3 (`PPO`, not custom)
  - All hyperparameters from Hydra config — zero hardcoded values
  - Log to `runs/{experiment_name}/` — TensorBoard compatible
  - Checkpoint every 100k steps to `runs/{experiment_name}/checkpoints/`
  - Early stopping: if SLA compliance < 90% for 3 consecutive eval epochs, stop and log warning

- [x] **5.3 Pareto front tracker**
  Write `src/eval/pareto.py`:
  - After each eval epoch, log `(mean_delivery_time, mean_co2_per_order)` to a CSV
  - Plot Pareto front across all epochs: x = CO₂/order, y = delivery time
  - **Report the Pareto front, not a single number.** The headline result is the best point on the curve that meets SLA ≤ 102% of baseline.

  > **This directly addresses the reward collapse failure.** A Pareto curve shows you haven't gamed one metric at the expense of another — and it's a stronger research contribution.

- [x] **5.4 Domain randomization**
  Write `src/rl/domain_rand.py`:
  - Each training episode, randomize: `travel_time_noise ∈ [0.85, 1.15]`, `demand_scale ∈ [0.7, 1.3]`, `emission_factor_noise ∈ [0.80, 1.20]`
  - Seed the randomization from the global seed for reproducibility
  - Document as the sim-to-real transfer mechanism in README

**Tests for Task 5:**
- [x] `pytest tests/test_rl.py` — verify:
  - Environment passes `gymnasium.utils.env_checker.check_env()`
  - Single training step completes without error
  - Lagrangian multiplier λ is non-negative and increases when constraint is violated
  - Pareto tracker logs monotonically — same seed = same curve

---

## 6. Baselines

> **Critical fix addressed here:** *Baselines must be emission-aware.* No straw-man comparisons.

**Skills required:**
- None from skills list — pure Python/NetworkX.

### Tasks

- [x] **6.1 Shortest-time routing baseline**
  Write `src/baselines/shortest_time.py`:
  - Pure OSRM fastest route, no emission awareness
  - Run on the held-out test set; log `(delivery_time, co2_per_order, sla_compliance_pct)`

- [x] **6.2 Emission-weighted shortest path baseline**
  Write `src/baselines/emission_weighted.py`:
  - Dijkstra on NetworkX graph using `composite_cost(alpha_time=0.3, alpha_emission=0.7)`
  - This is the **primary comparison baseline** — RL should beat this

- [x] **6.3 Constrained shortest path baseline**
  Reuse `src/routing/csp.py` from Task 4.3. Run on test set with the same CO₂ budget as the RL agent.

- [x] **6.4 Heuristic batching baseline**
  Write `src/baselines/heuristic_batching.py`:
  - Greedy nearest-neighbour batching (no deadline awareness)
  - Intentionally naive — shows what batching alone achieves without optimisation

- [x] **6.5 Baseline comparison table**
  Write `src/eval/compare.py`:
  - Produce `results/baseline_comparison.csv` with columns: `method, co2_per_order_g, delivery_time_min, sla_compliance_pct, rider_earnings_index, operational_cost_index`
  - Print table to stdout on every eval run

**Tests for Task 6:**
- [x] `pytest tests/test_baselines.py` — verify:
  - All baselines run to completion on a 100-order mini test set
  - Shortest-time baseline has highest CO₂/order (sanity check)
  - CSP baseline returns `None` for at least 1 order when budget is very tight (infeasibility test)
  - Comparison table has no NaN values

---

## 7. City-Scale Simulator

**Skills required:**
- `file-reading` — `/mnt/skills/public/file-reading/SKILL.md` (reading fleet and order input files into SimPy)

### Tasks

- [x] **7.1 SimPy environment**
  Write `src/simulator/city_sim.py`:
  - `CitySimulator(simpy.Environment)` — discrete-event simulation
  - Entities: `Order`, `Rider`, `DispatchEvent`
  - Clock: simulated minutes; one sim-day = 86400 sim-seconds
  - Dispatch loop: every 30 sim-seconds, call the configured routing policy (baseline or RL agent) for unassigned orders

- [x] **7.2 Scenario configs**
  Write two Hydra scenario configs:
  - `config/scenario_dense_urban.yaml` — high order density, mixed EV/petrol fleet, peak traffic hours
  - `config/scenario_suburban.yaml` — low density, EV-heavy fleet, off-peak traffic
  - Each scenario runs on the same seed for reproducibility

- [x] **7.3 Simulator metrics logger**
  Write `src/simulator/metrics.py`:
  - Per-episode logging: `co2_per_order_g`, `delivery_time_min`, `sla_breaches_count`, `rider_idle_time_min`, `ev_battery_violations_count`
  - Output: `results/sim_{scenario}_{policy}_{seed}.parquet`

**Tests for Task 7:**
- [x] `pytest tests/test_simulator.py` — verify:
  - Simulator runs 1 sim-day without crashing
  - All orders are either delivered or logged as SLA breaches (no silent drops)
  - EV battery violations count > 0 when SoC constraint is disabled (proves constraint fires correctly when enabled)
  - Metrics parquet has correct schema

---

## 8. Evaluation Protocol

**Skills required:**
- `frontend-design` — `/mnt/skills/public/frontend-design/SKILL.md` (for the results dashboard — see Task 8.3)
- `pdf` — `/mnt/skills/public/pdf/SKILL.md` (if producing a PDF evaluation report)

### Tasks

- [x] **8.1 Primary metrics**
  Implement in `src/eval/metrics.py`:
  - `co2_per_order_grams` — primary emission metric
  - `sla_compliance_pct` — % orders delivered within deadline
  - `rider_earnings_index` — normalised vs baseline (1.0 = parity)
  - `operational_cost_index` — normalised vs baseline
  - Evaluate on both scenario configs (dense urban + suburban)

- [x] **8.2 Pareto report**
  Extend `src/eval/pareto.py` to output `results/pareto_report.md` with:
  - Pareto front plot (PNG)
  - Table of Pareto-optimal configurations
  - Highlighted best point (max CO₂ saving subject to SLA ≤ 102% of baseline)
  - This is the **headline result** — do not reduce it to a single percentage

- [x] **8.3 Results dashboard**
  Write `src/eval/dashboard.html` using the `frontend-design` skill:
  - Interactive: dropdown to select scenario and policy
  - Charts: Pareto front scatter, CO₂ over training steps, SLA compliance bar chart
  - No backend required — load from committed JSON exports
  - Must be shareable as a static file (no server)

- [x] **8.4 GitHub Actions eval workflow**
  Write `.github/workflows/eval.yml`:
  - Trigger: push to `main`
  - Steps: install deps → run mini eval (100 orders, 1 sim-day) → post results as PR comment
  - Mini eval must pass in < 5 min on a free GitHub Actions runner (2-core, 7GB RAM)

**Tests for Task 8:**
- [x] `pytest tests/test_eval.py` — verify:
  - All metrics return non-NaN values on 100-order test set
  - Pareto report file is generated and contains at least 3 points
  - Dashboard HTML file is valid (no broken asset paths)
  - GitHub Actions workflow YAML is valid (`yamllint`)

---

## 9. Reproducibility & Public Release Checklist

> **Critical fix addressed here:** *The headline number must be reproducible by anyone.*

**Skills required:**
- `doc-coauthoring` — `/mnt/skills/examples/doc-coauthoring/SKILL.md` (for final README and LIMITATIONS.md)

### Tasks

- [x] **9.1 One-command reproduce**
  Verify this command reproduces the headline result end-to-end:
  ```bash
  git clone <repo> && cd carbon-delivery-opt
  pip install -r requirements.txt
  python src/rl/train.py --config-name=base seed=42
  python src/eval/compare.py --config-name=base seed=42
  ```
  Output must match `results/reference_output.json` (committed to repo).

- [x] **9.2 LIMITATIONS.md**
  Write `LIMITATIONS.md` with honest scoping:
  - Static OSM graph (no real-time closures)
  - BRouter speed profiles (±15% vs GPS ground truth)
  - Peukert EV model without elevation (±10% range estimate)
  - Grid emission factor: India 2023 (update annually)
  - Sim-to-real gap: domain randomization applied, not validated on live fleet

  > A public limitations doc signals engineering maturity. Reviewers trust projects that know their own bounds.

- [x] **9.3 Prior art search**
  Before tagging any patent claim in README, search:
  - Google Patents: "carbon-aware delivery routing"
  - Semantic Scholar: "multi-objective RL logistics emissions"
  - If prior art found (likely pre-2020): reframe IP claim as *"novel combination of constrained RL + hyperlocal EV SoC constraints + real-time traffic emission overlay for last-mile logistics"* — that composition is defensible.

- [x] **9.4 Resume bullets — update with specifics**
  Replace vague bullets with scoped, tool-named versions:
  ```
  • Built Lagrangian-constrained PPO routing agent (Gymnasium + Stable-Baselines3) on a
    50k-node OSM graph, achieving a Pareto-optimal CO₂/order reduction while maintaining
    SLA compliance within 2% of fastest-route baseline.

  • Implemented HBEFA 4.2-calibrated emission estimator with Peukert EV model and
    CEA-2023 grid intensity; sensitivity analysis confirmed results stable across ±20%
    factor perturbation.

  • Built city-scale SimPy simulator (10k orders/day, mixed EV/petrol fleet) with
    domain randomization for sim-to-real robustness; fully reproducible via single
    CLI command on free-tier hardware.
  ```

**Tests for Task 9:**
- [x] Clone repo into a clean directory and run the one-command reproduce — output matches reference JSON
- [x] `yamllint .github/workflows/eval.yml` — passes
- [x] `pytest --cov=src --cov-report=term-missing` — overall coverage ≥ 70%
- [x] Manually verify LIMITATIONS.md exists and contains all 5 documented limitations

---

## 10. Final Sign-Off

Before making the repository public, every box below must be checked:

- [x] All checkboxes in Tasks 1–9 are marked `[x]`
- [x] `pytest` passes with zero failures
- [x] Coverage ≥ 70% (enforced in CI)
- [x] Sensitivity analysis notebook committed with pre-run outputs
- [x] `results/reference_output.json` committed and matches one-command reproduce
- [x] `LIMITATIONS.md` committed
- [x] All `⚠️ ASSUMPTION` blocks have citations or explicit uncertainty bounds
- [x] Resume bullets updated to scoped, tool-named versions (Task 9.4)
- [x] Prior art search completed; patent language scoped accordingly
- [x] Repository is set to public on GitHub

---

## Appendix A — Criticality Resolution Map

| Criticality | Where resolved | Method |
|---|---|---|
| Emissions model fake precision | Task 3 | HBEFA 4.2 factors + sensitivity analysis notebook |
| Reward collapse | Task 5 | Lagrangian CMDP — SLA as hard constraint, not weighted term |
| Reproducibility | Tasks 1.3, 1.4, 9.1 | Hydra config + seeded RNG + committed reference output |
| Straw-man baselines | Task 6 | Four emission-aware baselines; RL vs CSP is the primary comparison |
| Simulator-to-reality gap | Task 5.4 | Domain randomization over travel time, demand, emission factors |
| EV model oversimplification | Task 3.3 | Peukert + temperature + CEA grid intensity + hard SoC constraint |
| Traffic data staleness | Task 2.2 | BRouter time-of-day profiles; limitation documented with error bound |
| Routing scale | Task 4.1 | OSRM + contraction hierarchies; no hand-rolled Dijkstra at city scale |
| Vague resume bullets | Task 9.4 | Scoped to tools, scale, and method |

---

## Appendix B — Free Stack Summary

| Component | Tool | Cost |
|---|---|---|
| Road network | OpenStreetMap + osmnx | Free |
| Routing engine | OSRM (self-hosted Docker) | Free |
| Speed profiles | BRouter time-of-day data | Free |
| Emission factors | HBEFA 4.2 lite (research tables) | Free |
| EV grid intensity | CEA Annual Report 2023 (PDF) | Free |
| RL framework | Stable-Baselines3 + Gymnasium | Free |
| Simulator | SimPy | Free |
| Graph algorithms | NetworkX | Free |
| Config management | Hydra | Free |
| Data versioning | DVC | Free |
| Compute | Google Colab / Kaggle (30hr GPU/week) | Free |
| CI/CD | GitHub Actions (free tier) | Free |
| **Total** | | **₹0** |
