import json
import pandas as pd

def compute_metrics(results_df, baseline_df=None):
    """
    Computes summary metrics from a DataFrame of order results.
    results_df must have: 'co2_per_order_g', 'is_sla_breach' (or 'delivery_time_min')
    """
    co2_per_order_grams = results_df['co2_per_order_g'].mean()
    delivery_time_min = results_df['delivery_time_min'].mean()
    
    if 'is_sla_breach' in results_df.columns:
        sla_compliance_pct = (1.0 - results_df['is_sla_breach'].mean()) * 100.0
    else:
        sla_compliance_pct = (results_df['delivery_time_min'] <= 30.0).mean() * 100.0
        
    rider_earnings_index = 1.0
    operational_cost_index = 1.0
    
    if baseline_df is not None:
        baseline_time = baseline_df['delivery_time_min'].mean()
        opt_time = results_df['delivery_time_min'].mean()
        
        rider_earnings_index = baseline_time / opt_time if opt_time > 0 else 1.0
        
        baseline_cost = baseline_df['co2_per_order_g'].mean()
        opt_cost = results_df['co2_per_order_g'].mean()
        operational_cost_index = opt_cost / baseline_cost if baseline_cost > 0 else 1.0
    
    # New metrics for enhanced dashboard
    fleet_mix = results_df['vehicle_type'].value_counts(normalize=True).to_dict() if 'vehicle_type' in results_df.columns else {}
    
    ev_trips = results_df[results_df['vehicle_type'] == 'ev_bike'] if 'vehicle_type' in results_df.columns else pd.DataFrame()
    mean_min_soc = ev_trips['final_soc'].mean() if not ev_trips.empty else 1.0
    
    hourly_co2 = results_df.groupby('hour_of_day')['co2_per_order_g'].mean().to_dict() if 'hour_of_day' in results_df.columns else {}

    return {
        'co2_per_order_grams': co2_per_order_grams,
        'delivery_time_min': delivery_time_min,
        'sla_compliance_pct': sla_compliance_pct,
        'rider_earnings_index': rider_earnings_index,
        'operational_cost_index': operational_cost_index,
        'fleet_mix_json': json.dumps(fleet_mix),
        'mean_min_soc': mean_min_soc,
        'hourly_co2_json': json.dumps(hourly_co2)
    }
