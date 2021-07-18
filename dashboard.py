# %%

from keplergl import KeplerGl
map_ = KeplerGl(height=500)
map_

# %%
map_.add_data(data=gdf_lines, name="segments")

# %%
import geopandas as gpd

# %%
with open('kepler_config.json', 'w') as f:
    f.write(map_.config)

# %%
with open('kepler_config.json', 'w') as f:
    f.write(map_.config)
