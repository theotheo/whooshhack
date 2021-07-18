# %%
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point, LineString, shape
from pathlib import Path
import datetime as dt
import dask.dataframe as dd

# %%
def create_datetime(date, time_str):
    if len(time_str) == 5:
        time_str = f'{time_str}:00.000'
    time = dt.datetime.strptime(time_str, '%H:%M:%S.%f').time()
    return dt.datetime.combine(date, time)

dfs = []
for fn in Path('scooter').glob('*.csv'):
    print(fn)
    # df = pd.read_csv(f"{fn}")
    ddf = dd.read_csv(fn, )
    df = ddf.compute()
    date = dt.datetime.strptime(str(fn.name), 'ks_track_%Y-%m-%d.csv')
    # df['ride_id'] = f'{date}-{df["ride_id"]}'
    df['ride_id'] = df["gps_date"].str[5:] + "-" + df["ride_id"].astype('str')

    df['dt'] = df['gps_t'].apply(lambda t: create_datetime(date, t))
    dfs.append(df)

df = pd.concat(dfs)

df = df.sort_values(['ride_id', 'dt'])
df.to_csv('scooter.csv', index=False)
# df.to_csv('scooter.csv.gz', compression='gzip')

