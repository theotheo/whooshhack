# %%

from keplergl import KeplerGl
map_ = KeplerGl(height=500)
map_

# %%
map_.add_data(data=gdf_lines, name="segments")

# %%
import geopandas as gpd
gpd.read_file('sample_route2.json')

# %%
points = gpd.read_file('points_sample.json')
map_.add_data(data=points, name='points')

# %%
map_

# %%
with open('kepler_config.json', 'w') as f:
    f.write(map_.config)

# %%
with open('kepler_config.json', 'w') as f:
    f.write(map_.config)
