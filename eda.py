# %%
import lux
import modin.pandas as pd 
from shapely.geometry import LineString, Point, Polygon
import geopandas as gpd
from routingpy import Valhalla
from routingpy.exceptions import RouterApiError
from pprint import pprint
from collections import defaultdict
# pd.set_option("plotting.backend", "pandas_bokeh")
# pd.options.plotting.backend = "plotly"
import numpy as np
np.random.seed(0)
# %%
df = pd.read_csv('scooter.csv')
# %%
df['gps_date'].hist(xrot=90)

# %%
ids = df['ride_id'].unique()
sample_ids = np.random.choice(ids, 100)
sample_df = df[df['ride_id'].isin(sample_ids)]
sample_df['gps_date'].hist(xrot=90)

# %%

# %%
import skmob
skmob.core.trajectorydataframe.np.random.seed(0)
tdf = skmob.TrajDataFrame(sample_df._to_pandas(), latitude='lat', longitude='lon', datetime='dt', user_id='ride_id')

# %%
tdf.head()

# %%
tdf.plot_trajectory()

# %%
from skmob.preprocessing import detection
tdf._crs = {'init': 'epsg:4326'}
stdf = detection.stops(tdf, stop_radius_factor=0.5, minutes_for_a_stop=0.5, spatial_radius_km=0.005, leaving_time=True)
stdf.head()

# %%
from skmob.preprocessing import compression
# compress the trajectory using a spatial radius of 0.2 km
ctdf = compression.compress(tdf, spatial_radius_km=0.2)
print('Points of the original trajectory:\t%s'%len(tdf))
print('Points of the compressed trajectory:\t%s'%len(ctdf))

# %%
coords = [[37.468610, 55.682627], [37.622663, 55.669160, ]]
client = Valhalla(base_url='http://localhost:8002')


def get_route(coords, profile):

    route = client.directions(locations=coords, profile=profile)
# isochrones = client.isochrones(locations=coords[0], profile='pedestrian', intervals=[600, 1200])
# matrix = client.matrix(locations=coords, profile='pedestrian')

    # pprint((route.geometry, route.duration, route.distance, route.raw))
    # pprint((isochrones.raw, isochrones[0].geometry, isochrones[0].center, isochrones[0].interval))
    # pprint((matrix.durations, matrix.distances, matrix.raw))


    start_end = gpd.GeoDataFrame(geometry=[Point(x,y) for x,y in coords], crs="EPSG:4326")#.to_crs("EPSG:3857")
    route_line = gpd.GeoDataFrame(geometry=[LineString(route.geometry)], crs="EPSG:4326")#.to_crs("EPSG:3857")

    # route_line.to_file('sample_route2.json', driver='GeoJSON')
    return route_line

# get_route(coords, 'auto')
# %%
planned_routes = defaultdict(list)
for profile in ['pedestrian', 'auto']:
    for ride_id, group in sample_df.groupby('ride_id'):
        print(ride_id)
        start = group.iloc[0]
        end = group.iloc[-1]
        try:     
            route = get_route([[start.lon, start.lat], [end.lon, end.lat]], profile)
            planned_routes[profile].append({'ride_id': ride_id, 'geometry': route['geometry'].iloc[0]})

        # group.apply(lambda s: get_route(s.first['lat'], ))
        except RouterApiError:
            route = None
            print('error: ', ride_id)
            planned_routes[profile].append({'ride_id': ride_id, 'geometry': None})
            

# %%
auto_planned = gpd.GeoDataFrame(planned_routes['auto'], geometry='geometry')
pedestrian_planned = gpd.GeoDataFrame(planned_routes['pedestrian'], geometry='geometry')

# %%
# %%
auto_planned.set_crs("EPSG:4326").to_crs("EPSG:3857").geometry.length

# %%
auto_planned.to_file('auto_planned.json', driver='GeoJSON')
pedestrian_planned.to_file('pedestrian_planned.json', driver='GeoJSON')

# %% ОТРЕЗКИ ПУТИ


from convert_to_trips import points_to_trip

sample_df['dt'] = pd.to_datetime(sample_df['dt']) 
sample_trip_df = points_to_trip(sample_df)

# %%
sample_trip_df.to_file('sample_trips.json', driver='GeoJSON')

# %%
# %%
distance_df = pd.DataFrame()
distance_df['ride_id'] = sample_trip_df['ride_id']
distance_df['auto'] = auto_planned.set_crs("EPSG:4326").to_crs("EPSG:3857").geometry.length
distance_df['pedestrian'] = pedestrian_planned.set_crs("EPSG:4326").to_crs("EPSG:3857").geometry.length
distance_df['reality'] = sample_trip_df.set_crs("EPSG:4326").to_crs("EPSG:3857").geometry.length




def dist(s):
    return Point(s.coords[0]).distance(Point(s.coords[-1]))
distance_df['abs'] = sample_trip_df.set_crs("EPSG:4326").to_crs("EPSG:3857").geometry.apply(lambda t: dist(t))

distance_df['circle'] = distance_df['reality'] - distance_df['abs'] 
distance_df

# %%
distance_df['r-p'] = distance_df['reality'] - distance_df['pedestrian'] 
distance_df['r-a'] = distance_df['reality'] - distance_df['auto'] 
distance_df['r-p'].hist()

# %%

segments_dfs = []
for ride_id, group in sample_df._to_pandas().groupby('ride_id'):
    shifted = group.shift()

    

    
    lines = [LineString([(lon1, lat1), (lon2, lat2)]) for lat1, lon1, lat2, lon2 in zip(group.lat, group.lon, shifted.lat, shifted.lon) if lon1]
    dv = group['wheel'] - shifted['wheel']
    
    lines_df['ride_id'] = ride_id

    lines_df = gpd.GeoDataFrame(geometry=lines, crs="EPSG:4326")
    # print(len(lines), len(dv[1:]), len(distance[1:]))
    # lines_df['geometry'] = lines
    lines_df = lines_df.to_crs("EPSG:3857")
    distance =  lines_df.geometry.length
    print(dv, distance)

    
    lines_df['dv'] = dv
    print(len(distance), len(dv))
    # lines_df['acceleration'] = dv / distance
        # distance = group.geometry.distance(shifted.geometry)

    # lines_df['acceleration'] = lines_df['acceleration'].fillna(0)
    # print(df)
    lines_df['acceleration'] = lines_df['dv'] / distance
    # lines_df['acceleration'] = lines_df['acceleration'].fillna(0)
    segments_dfs.append(lines_df)
    break
# %%

all_lines = pd.concat(segments_dfs)

gdf_lines = gpd.GeoDataFrame(all_lines._to_pandas(), geometry='geometry') 
gdf_lines.to_crs("EPSG:4326").to_file('sample_segments1.json', driver='GeoJSON')
