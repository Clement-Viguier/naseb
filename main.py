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

tol = 0.01


def main():

    data = pd.read_csv(
        './data/canéjan interpolé 1992-01-01 to 2022-12-31.csv')
    model_pet_visual_crossing(data)

    model_list = [
        "surf_park_no_city_water",
        "surf_park_city_water",
        "surf_park_city_water_surfers",
        "surf_park_monthly_avg",
        "surf_park_monthly",
    ]

    index_dict = {
        "surf_park_mensuel_copy": MONTHLY_INDEX,
        "surf_park_monthly": MONTHLY_INDEX_30_YEARS
    }

    variations = {
        "baseline": {},
        "low_harvest": {"parameters": {
            "recuperation_factor": {
                "name": "recuperation_factor",
                "type": "constant",
                "value": 0.6
            }}
        },
        "medium_evap": {"parameters": {
            "pet_penalty_factor": {
                "name": "pet_penalty_factor",
                "type": "constant",
                "value": 1.3,
            }}
        },
        "high_evap": {"parameters": {
            "pet_penalty_factor": {
                "name": "pet_penalty_factor",
                "type": "constant",
                "value": 1.7,
            }}
        },
        "high_evap_low_harvest": {"parameters": {
            "pet_penalty_factor": {
                "name": "pet_penalty_factor",
                "type": "constant",
                "value": 1.7,
            },
            "recuperation_factor": {
                "name": "recuperation_factor",
                "type": "constant",
                "value": 0.6
            }}
        },
        # "flow_limit":{} # add flow limits to the system's bottlenecks
    }

    # TODO need to check the link tampon -> rainwater_storage (other way around in schematics, but their sim assume such a link)

    agg_fct = {
        "bassin_volume": [np.mean, np.median],
        "city_link_flow": [np.mean, np.sum],
        "pet_flow": [np.mean],
        "surfer_water_flow": [np.mean, np.sum],
        "capacity_group": [np.mean, np.median]
    }

    sim_list = []
    for model_name in model_list:
        for variation, extra_params in variations.items():
            print(f"Model: {model_name} - {variation}")
            model_path = f"./models/{model_name}.json"
            sim_df = model_surf_park(
                model_path, index=index_dict.get(model_name, None), extra_params=extra_params)
            sim_df.to_csv(f'./sim/sim_{model_name}_{variation}.csv')

            print(sim_df['bassin_volume'].describe())

            sim_df['capacity_group'] = pd.cut(sim_df['bassin_volume'], [
                0, VOLUME_BASSIN2*(1-tol), VOLUME_BASSIN1*(1-tol), (VOLUME_BASSIN1+VOLUME_BASSIN2)*(1-tol)])

            sim_df['variation'] = variation
            sim_df['model_name'] = model_name

            sim_list.append(sim_df)

    all_sims = pd.concat(sim_list)
    # print(all_sims)

    sim_summary = all_sims.groupby(
        ['variation', 'model_name']).aggregate(agg_fct)

    print(sim_summary)
    sim_summary.to_csv('./sim/summary.csv')


if __name__ == "__main__":
    main()
