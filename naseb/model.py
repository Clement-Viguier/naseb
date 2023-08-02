
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

    return data


def model_pet_visual_crossing(data, path='./data/weather_data.csv', site_latitude=44.77779995110141, site_elevation=900):

    # model PET

    data = enrich_data(data)

    print(data.describe())
    used_columns = ['temp', 'windspeed', 'tempmin', 'tempmax', 'humidity',
                    'solarenergy', 'sealevelpressure', 'solarradiation']
    data[used_columns] = data[used_columns].fillna(method='bfill')

    int_columns = ["sealevelpressure"]
    data[int_columns] = data[int_columns].astype(int)

    data["pet_penman"] = penman(
        tmean=data['temp'],
        wind=data['windspeed'],
        tmin=data['tempmin'],
        tmax=data['tempmax'],
        rh=data['humidity'],
        rn=data['solarenergy'],
        pressure=data['sealevelpressure'],
        n=data['hours_of_daylight'],
        elevation=site_elevation,
        lat=np.deg2rad(site_latitude),
    )

    if (path is not None):
        data.to_csv(path)

    return data


def model_surf_park():

    m = Model.load("./models/hydropower_example.json")
    m = Model.load("./models/proto_example.json")

    stats = m.run()
    print(stats)

    # print(m.recorders["turbine1_energy"].values())

    df = m.to_dataframe()
    print(df.head(30))

    from matplotlib import pyplot as plt

    df.plot(subplots=True)
    plt.show()
