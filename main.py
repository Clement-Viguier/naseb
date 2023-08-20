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


def main():

    data = pd.read_csv(
        './data/canéjan interpolé 1992-01-01 to 2022-12-31.csv')
    model_pet_visual_crossing(data)

    model_list = [
        "surf_park_no_city_water",
        "surf_park_city_water",
        "surf_park_monthly_avg",
    ]

    index_dict = {
        "surf_park_mensuel_copy": MONTHLY_INDEX,
    }

    for model_name in model_list:
        model_path = f"./models/{model_name}.json"
        sim_df = model_surf_park(
            model_path, index=index_dict.get(model_name, None))
        sim_df.to_csv(f'./sim/sim_{model_name}.csv')


if __name__ == "__main__":
    main()
