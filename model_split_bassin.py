from naseb.model import model_surf_park, model_pet_visual_crossing
import numpy as np
import pandas as pd

MONTHLY_INDEX = [
    "1992-01-01",
    "1992-02-01",
    "1992-03-01",
    "1992-04-01",
    "1992-05-01",
    "1992-06-01",
    "1992-07-01",
    "1992-08-01",
    "1992-09-01",
    "1992-10-01",
    "1992-11-01",
    "1992-12-01",
]

MONTHLY_INDEX_30_YEARS = pd.read_csv('./data/monthly_data.csv')['date']


VOLUME_BASSIN1 = 13000
VOLUME_BASSIN2 = 7000

BASSIN_TOTAL_AREA = 13548

tol = 0.01

data = pd.read_csv(
    './data/canéjan interpolé 1992-01-01 to 2022-12-31.csv')
model_pet_visual_crossing(data)

model_list = [
    "surf_park_no_city_water_split",
]

index_dict = {
    "surf_park_mensuel_copy": MONTHLY_INDEX,
    "surf_park_monthly": MONTHLY_INDEX_30_YEARS
}

variations = {
    "baseline": {},
    # "medium_evap": {"parameters": {
    #     "pet_penalty_factor": {
    #         "name": "pet_penalty_factor",
    #         "type": "constant",
    #         "value": 1.3,
    #     }}
    # },
    "high_evap": {"parameters": {
        "pet_penalty_factor": {
            "name": "pet_penalty_factor",
            "type": "constant",
            "value": 1.7,
        }}
    },
    # "flow_limit":{} # add flow limits to the system's bottlenecks
}

# TODO need to check the link tampon -> rainwater_storage (other way around in schematics, but their sim assume such a link)

agg_fct = {
    "bassin1_volume": [np.mean, np.median],
    "bassin2_volume": [np.mean, np.median],
    "pet_b1_flow": [np.mean],
    "pet_b2_flow": [np.mean],
    "capacity": [np.mean, np.median]
}

sim_list = []
for model_name in model_list:
    for variation, extra_params in variations.items():
        print(f"Model: {model_name} - {variation}")
        model_path = f"./models/{model_name}.json"
        sim_df = model_surf_park(
            model_path, index=index_dict.get(model_name, None), extra_params=extra_params)
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

        sim_df.to_csv(f'./sim/sim_{model_name}_{variation}.csv')
        sim_list.append(sim_df)

all_sims = pd.concat(sim_list)
print(all_sims['capacity_group'])

sim_summary = all_sims.groupby(
    ['variation', 'model_name']).aggregate(agg_fct)
sim_summary.columns = sim_summary.columns.map('|'.join).str.strip('|')
print(sim_summary)
sim_summary.to_csv('./sim/summary_split.csv')
