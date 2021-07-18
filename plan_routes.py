# %%
from shapely.geometry import LineString, Point, Polygon
import geopandas as gpd
from routingpy import Valhalla
from pprint import pprint

coords = [[37.619561, 55.775573], [37.622278, 55.724296],
        #   [13.453649, 52.507987], [13.401947, 52.543373]
          ]
coords = [[37.750817, 55.763528], [37.571776, 55.709682, ]]

coords = [[37.468610, 55.682627], [37.622663, 55.669160, ]]

client = Valhalla(base_url='http://localhost:8002')

# %%
route = client.directions(locations=coords, profile='pedestrian')
# isochrones = client.isochrones(locations=coords[0], profile='pedestrian', intervals=[600, 1200])
# matrix = client.matrix(locations=coords, profile='pedestrian')

pprint((route.geometry, route.duration, route.distance, route.raw))
# pprint((isochrones.raw, isochrones[0].geometry, isochrones[0].center, isochrones[0].interval))
# pprint((matrix.durations, matrix.distances, matrix.raw))


start_end = gpd.GeoDataFrame(geometry=[Point(x,y) for x,y in coords], crs="EPSG:4326")#.to_crs("EPSG:3857")
route_line = gpd.GeoDataFrame(geometry=[LineString(route.geometry)], crs="EPSG:4326")#.to_crs("EPSG:3857")

route_line.to_file('sample_route2.json', driver='GeoJSON')
# %%
route_line