from naseb.model import model_surf_park, model_pet_visual_crossing
import numpy as np
import pandas as pd

VOLUME_BASSIN1 = 13000
VOLUME_BASSIN2 = 7000

BASSIN_TOTAL_AREA = 13548

tol = 0.01

# technically only necessary once
data = pd.read_csv(
    './data/canéjan interpolé 1992-01-01 to 2022-12-31.csv')
model_pet_visual_crossing(data)

model_list = [
    "surf_park_no_city_water_split",
    "surf_park_no_city_water_split_meteofrance_merignac",
    "surf_park_city_water_split_meteofrance_merignac",
]

variations = {
    "baseline": {},
    "high_evap": {"parameters": {
        "pet_penalty_factor": {
            "name": "pet_penalty_factor",
            "type": "constant",
            "value": 1.7,
        }}
    },
    # "flow_limit":{} # add flow limits to the system's bottlenecks
}

agg_fct = {
    "bassin1_volume": [np.mean, np.median],
    "bassin2_volume": [np.mean, np.median],
    "pet_b1_flow": [np.mean],
    "pet_b2_flow": [np.mean],
    "capacity": [np.mean, np.median],
    "city_link_flow": [np.mean, np.sum]
}

sim_list = []
# run the simulation for each model and parameter variant
for model_name in model_list:
    for variation, extra_params in variations.items():
        print(f"Model: {model_name} - {variation}")
        model_path = f"./models/{model_name}.json"
        sim_df = model_surf_park(
            model_path, index=None, extra_params=extra_params)

        # compute additional features
        sim_df['bassin_volume'] = sim_df['bassin1_volume'] + \
            sim_df['bassin2_volume']
        sim_df['pet_flow'] = sim_df['pet_b1_flow'] + \
            sim_df['pet_b2_flow']
        sim_df['bassin_rainwater_flow'] = sim_df['bassin1_rainwater_flow'] + \
            sim_df["bassin2_rainwater_flow"]
        print(sim_df['bassin_volume'].describe())
        cuts = [
            0, VOLUME_BASSIN2*(1-tol), VOLUME_BASSIN1*(1-tol), (VOLUME_BASSIN1+VOLUME_BASSIN2)*(1-tol)]
        sim_df['capacity_group'] = pd.cut(
            sim_df['bassin_volume'], cuts+[np.inf], labels=cuts)
        sim_df['capacity'] = sim_df['capacity_group'].astype(
            float)/(VOLUME_BASSIN1+VOLUME_BASSIN2)

        sim_df['variation'] = variation
        sim_df['model_name'] = model_name

        # save the simulation data
        sim_df.to_csv(f'./sim/sim_{model_name}_{variation}.csv')
        sim_list.append(sim_df)

all_sims = pd.concat(sim_list)
print(all_sims['capacity_group'])

# summary statistics
sim_summary = all_sims.groupby(
    ['variation', 'model_name']).aggregate(agg_fct)
sim_summary.columns = sim_summary.columns.map('|'.join).str.strip('|')
print(sim_summary)
sim_summary.to_csv('./sim/summary_split.csv')
