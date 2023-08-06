
import os
import pandas as pd
import networkx as nx
import numpy as np

from pywr.model import Model
from pyet.combination import penman
# from pywr.nodes import Input, Output, Link

# name,datetime,tempmax,tempmin,temp,feelslikemax,feelslikemin,feelslike,dew,humidity,
# precip,precipprob,precipcover,preciptype,snow,snowdepth,windgust,windspeed,winddir,
# sealevelpressure,cloudcover,visibility,solarradiation,solarenergy,uvindex,severerisk,
# sunrise,sunset,moonphase,conditions,description,icon,stations


def enrich_data(data):

    data['hours_of_daylight'] = (pd.to_datetime(
        data['sunset'])-pd.to_datetime(data['sunrise'])).dt.total_seconds()/3600

    data['datetime'] = pd.to_datetime(data['datetime'])
    data['dayofyear'] = data['datetime'].dt.day_of_year

    solar_energy_map = data.groupby(
        'dayofyear')['solarenergy'].mean().to_dict()

    data.loc[data['solarenergy'].isna(), 'solarenergy'] = [solar_energy_map.get(
        day) for day in data.loc[data['solarenergy'].isna(), 'dayofyear']]

    solar_radiation_map = data.groupby(
        'dayofyear')['solarradiation'].mean().to_dict()

    data.loc[data['solarradiation'].isna(), 'solarradiation'] = [solar_radiation_map.get(
        day) for day in data.loc[data['solarradiation'].isna(), 'dayofyear']]

    return data


def model_pet_visual_crossing(data, path='./data/weather_data.csv', site_latitude=44.77779995110141, site_elevation=900):

    # model PET

    data = enrich_data(data)

    used_columns = ['temp', 'windspeed', 'tempmin', 'tempmax', 'humidity',
                    'sealevelpressure', 'precip']
    data[used_columns] = data[used_columns].fillna(method='bfill')

    int_columns = ["sealevelpressure"]
    data[int_columns] = data[int_columns].astype(int)

    data["pet_penman"] = penman(
        tmean=data['temp'],
        wind=data['windspeed']/3.6,
        tmin=data['tempmin'],
        tmax=data['tempmax'],
        rh=data['humidity'],
        rn=data['solarenergy'],
        rs=data['solarradiation']*0.0864,
        pressure=data['sealevelpressure']/10,
        n=data['hours_of_daylight'],
        elevation=site_elevation,
        lat=np.deg2rad(site_latitude),
    )
    data["pet_kimberly_penman"] = penman(
        tmean=data['temp'],
        wind=data['windspeed']/3.6,
        tmin=data['tempmin'],
        tmax=data['tempmax'],
        rh=data['humidity'],
        rn=data['solarenergy'],
        rs=data['solarradiation']*0.0864,
        pressure=data['sealevelpressure']/10,
        n=data['hours_of_daylight'],
        elevation=site_elevation,
        lat=np.deg2rad(site_latitude),
    )

    data['pet_corrected'] = data['pet_penman']/2

    # data['pet_corrected'] = data['pet_corrected'].fillna(method='bfill')
    print(data.describe())

    if (path is not None):
        data.to_csv(path)

    return data


def model_surf_park():

    m = Model.load("./models/hydropower_example.json")
    m = Model.load("./models/proto_example.json")
    m = Model.load("./models/surf_park_city_water.json")
    m = Model.load("./models/surf_park_mensuel.json")

    # print(draw_graph(m)) # only works in notebook

    stats = m.run()
    print(stats)

    # print(m.recorders["turbine1_energy"].values())

    df = m.to_dataframe()
    print(df.head(30))

    from matplotlib import pyplot as plt

    df.plot(subplots=True)
    plt.show()
