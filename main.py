from naseb.model import model_surf_park, model_pet_visual_crossing
import pandas as pd


def main():
    data = pd.read_csv(
        './data/canéjan interpolé 1992-01-01 to 2022-12-31.csv')
    model_pet_visual_crossing(data)
    model_surf_park()


if __name__ == "__main__":
    main()
