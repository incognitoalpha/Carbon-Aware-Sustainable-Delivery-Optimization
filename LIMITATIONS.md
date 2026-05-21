# Limitations

While this project demonstrates a significant optimization in carbon-aware delivery routing, it is subject to the following limitations:

1. **Static OSM graph (no real-time closures):** The road network is based on a static OpenStreetMap export. Dynamic events such as road closures, accidents, or temporary traffic restrictions are not modeled in this version.
2. **BRouter speed profiles (±15% vs GPS ground truth):** Traffic speed overlays rely on city-class averages derived from BRouter time-of-day data. While robust, these profiles carry an estimated error bound of ±15% compared to GPS-trace-calibrated ground truth.
3. **Peukert EV model without elevation (±10% range estimate):** The Electric Vehicle state-of-charge (SoC) model incorporates Peukert's law and temperature penalties but currently omits high-resolution elevation data. This simplification may result in a ±10% variance in actual range estimates on steep terrains.
4. **Grid emission factor: India 2023 (update annually):** The indirect emissions for EV charging are calculated using the Central Electricity Authority (CEA) of India's 2023 grid intensity factor (708 g CO₂/kWh). This factor should be updated annually or localized for different regions.
5. **Sim-to-real gap:** Although domain randomization is applied during training to enhance the robustness of the RL agent against variations in travel time, demand, and emission factors, the policy has not yet been validated on a live operational fleet.
