# %%
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point, LineString, shape
from pathlib import Path
import datetime as dt
import dask.dataframe as dd
import lux

# %%

def convert_to_lines(df):
    rides = []

    for ride_id, group in df.groupby('ride_id'):
        if group.shape[0] < 2:
            print(ride_id)
            continue
    
        # print(ride_id)
        ride = {}
        ride['geometry'] = LineString([Point(xy) for xy in zip(group.lon, group.lat)])
        # geo_df = gpd.GeoDataFrame(group, geometry=geometry)
        ride['mean_wheel'] = group.wheel.mean()
        ride['median_wheel'] = group.wheel.median()
        ride['std_wheel'] = group.wheel.std()

        start_time = group.dt.min()
        end_time = group.dt.max()
        ride['start_time'] = start_time
        ride['end_time'] = end_time

        duration = end_time - start_time
        ride['duration'] = np.round(duration.total_seconds() / 60, 1)
        ride['ride_id'] = ride_id

        rides.append(ride)

    gdf = gpd.GeoDataFrame(rides)
    return gdf
# %%
ddf = dd.read_csv('scooter.csv', parse_dates=['dt'])
df = ddf.compute()


lines_gdf = convert_to_lines(df)

# %%
lines_gdf.to_file('scooter_trips.json', driver="GeoJSON")
# %%

# %%
sample_df = df[:10000]
gdf_points = gpd.GeoDataFrame(
    sample_df, geometry=gpd.points_from_xy(sample_df.lon, sample_df.lat))

# gdf_points
