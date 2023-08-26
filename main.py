from naseb.model import model_surf_park, model_pet_visual_crossing
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


def main():

    data = pd.read_csv(
        './data/canéjan interpolé 1992-01-01 to 2022-12-31.csv')
    model_pet_visual_crossing(data)

    model_list = [
        "surf_park_no_city_water",
        "surf_park_city_water",
        "surf_park_monthly_avg",
        "surf_park_monthly",
    ]

    index_dict = {
        "surf_park_mensuel_copy": MONTHLY_INDEX,
        "surf_park_monthly": MONTHLY_INDEX_30_YEARS
    }

    variations = {
        "baseline": {},
        "high_evap": {},
        "low_harvest": {},
        "high_evap_low_harvest": {},
        # "flow_limit":{} # add flow limits to the system's bottlenecks
    }

    for model_name in model_list:
        for variation, extra_params in variations.items():
            model_path = f"./models/{model_name}.json"
            sim_df = model_surf_park(
                model_path, index=index_dict.get(model_name, None), extra_params=extra_params)
            sim_df.to_csv(f'./sim/sim_{model_name}_{variation}.csv')


if __name__ == "__main__":
    main()
