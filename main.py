from naseb.model import model_surf_park, model_pet_visual_crossing
import pandas as pd


def main():

    data = pd.read_csv(
        './data/canéjan interpolé 1992-01-01 to 2022-12-31.csv')
    model_pet_visual_crossing(data)

    model_list = [
        "proto_example",
        "surf_park_city_water",
        "surf_park_mensuel_copy",
    ]

    for model_name in model_list:
        model_path = f"./models/{model_name}.json"
        sim_df = model_surf_park(model_path)
        sim_df.to_csv(f'./sim/sim_{model_name}.csv')


if __name__ == "__main__":
    main()
