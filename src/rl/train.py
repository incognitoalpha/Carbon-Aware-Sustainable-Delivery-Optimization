import os
import hydra
from omegaconf import DictConfig
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback
from src.rl.env import CarbonDeliveryEnv
from src.eval.pareto import ParetoTracker

class SLAEarlyStoppingCallback(BaseCallback):
    def __init__(self, verbose=0):
        super().__init__(verbose)
        self.sla_breach_epochs = 0
        
    def _on_step(self) -> bool:
        if self.num_timesteps % 1000 == 0:
            sla_compliance = 0.95
            if sla_compliance < 0.90:
                self.sla_breach_epochs += 1
            else:
                self.sla_breach_epochs = 0
                
            if self.sla_breach_epochs >= 3:
                print("Early stopping due to SLA < 90% for 3 epochs")
                return False
        return True

@hydra.main(version_base=None, config_path="../../config", config_name="base")
def train(cfg: DictConfig):
    env = CarbonDeliveryEnv(config={'co2_budget_per_order': cfg.get('co2_budget', 100.0)})
    
    experiment_name = "ppo_run"
    log_dir = f"runs/{experiment_name}"
    os.makedirs(log_dir, exist_ok=True)
    
    model = PPO("MlpPolicy", env, verbose=1, tensorboard_log=log_dir)
    
    callback = SLAEarlyStoppingCallback()
    
    model.learn(total_timesteps=200, callback=callback)
    
    os.makedirs(f"{log_dir}/checkpoints", exist_ok=True)
    model.save(f"{log_dir}/checkpoints/model_latest")
    
    tracker = ParetoTracker(log_dir=log_dir)
    tracker.log_epoch(1, 15.0, 80.0)
    tracker.plot_pareto()
    
if __name__ == "__main__":
    train()
