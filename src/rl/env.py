import gymnasium as gym
import numpy as np
from gymnasium import spaces

class CarbonDeliveryEnv(gym.Env):
    def __init__(self, config=None):
        super().__init__()
        self.config = config or {}
        self.co2_budget_per_order = self.config.get('co2_budget_per_order', 100.0)
        
        # State: [pickup_dist, deadline_rem, rider_soc, vehicle_type, traffic_intensity, temp]
        low = np.array([0.0, 0.0, 0.0, 0.0, 0.0, -10.0], dtype=np.float32)
        high = np.array([10000.0, 120.0, 1.0, 2.0, 2.0, 50.0], dtype=np.float32)
        self.observation_space = spaces.Box(low=low, high=high, dtype=np.float32)
        
        # Action space: Discrete(3)
        self.action_space = spaces.Discrete(3)
        
        self.lagrangian_multiplier = 0.0
        self.learning_rate_lambda = 0.01
        
        self._current_step = 0
        self._max_steps = 100

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self._current_step = 0
        
        obs = np.array([1500.0, 45.0, 0.8, 1.0, 1.0, 25.0], dtype=np.float32)
        info = {}
        return obs, info

    def step(self, action):
        self._current_step += 1
        
        # Mock action effects
        delivery_time_minutes = 15.0 + action * 5.0
        grams_co2 = 120.0 - action * 30.0
        
        reward = -delivery_time_minutes
        
        constraint_violation = grams_co2 - self.co2_budget_per_order
        penalty = self.lagrangian_multiplier * max(0, constraint_violation)
        
        total_reward = reward - penalty
        
        self.lagrangian_multiplier += self.learning_rate_lambda * constraint_violation
        self.lagrangian_multiplier = max(0.0, self.lagrangian_multiplier)
        
        terminated = self._current_step >= self._max_steps
        truncated = False
        
        obs = np.array([1000.0, 30.0, 0.7, 1.0, 1.2, 26.0], dtype=np.float32)
        
        info = {
            'delivery_time_minutes': delivery_time_minutes,
            'grams_co2': grams_co2,
            'constraint_violation': constraint_violation
        }
        
        return obs, total_reward, terminated, truncated, info

    def render(self):
        print(f"Step: {self._current_step}, Lambda: {self.lagrangian_multiplier:.4f}")
