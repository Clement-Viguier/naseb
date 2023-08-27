import copy
import os
import json
import pandas as pd
import networkx as nx
import numpy as np


from pywr.model import Model
from pyet.combination import penman
# from pywr.nodes import Input, Output, Link

from .utils import update_nested

# name,datetime,tempmax,tempmin,temp,feelslikemax,feelslikemin,feelslike,dew,humidity,
# precip,precipprob,precipcover,preciptype,snow,snowdepth,windgust,windspeed,winddir,
# sealevelpressure,cloudcover,visibility,solarradiation,solarenergy,uvindex,severerisk,
# sunrise,sunset,moonphase,conditions,description,icon,stations


def add_time_columns(data, datetime_column: str | None = None):
    if datetime_column is None:
        datetime_column = 'datetime'

    data[datetime_column] = pd.to_datetime(data[datetime_column])
    data['dayofyear'] = data[datetime_column].dt.day_of_year
    data['year'] = data[datetime_column].dt.year
    data['month'] = data[datetime_column].dt.month
    data['weekofyear'] = data[datetime_column].dt.isocalendar().week
    return data


def enrich_data(data):

    data['hours_of_daylight'] = (pd.to_datetime(
        data['sunset'])-pd.to_datetime(data['sunrise'])).dt.total_seconds()/3600

    data = add_time_columns(data)

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


def model_surf_park(model_path: str | None = None, index: str or None = None, extra_params: dict | None = None):

    # m = Model.load("./models/hydropower_example.json")
    # m = Model.load("./models/proto_example.json")
    # m = Model.load("./models/surf_park_city_water.json")
    if model_path is None:
        model_path = "./models/surf_park_mensuel_copy.json"
    with open(model_path, 'r') as m:
        model_json = json.load(m)

    old_model = copy.deepcopy(model_json)

    if extra_params:
        model_json = update_nested(model_json, extra_params)

    m = Model.load(model_json)
    # print(model_json)
    stats = m.run()
    # print(stats)

    df = m.to_dataframe()
    df = df.droplevel(1, axis=1)
    df.reset_index(drop=False, inplace=True)
    print(df['index'].dtype)
    if index is not None:
        df['index'] = pd.to_datetime(index)
    else:
        df['index'] = df['index'].dt.to_timestamp()

    # print(df.head(30))
    df = add_time_columns(df, 'index')

    return df
