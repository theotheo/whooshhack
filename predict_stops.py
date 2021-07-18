# %%
import modin.pandas as pd
import geopandas as gpd
import trackintel as ti

df = pd.read_csv("scooter.csv")
sample_df = df[:100000]
gdf_points = gpd.GeoDataFrame(
    sample_df, geometry=gpd.points_from_xy(sample_df.lon, sample_df.lat))

pfs = ti.io.from_geopandas.read_positionfixes_gpd(gdf_points, tracked_at='dt', user_id='ride_id', geom_col='geometry', tz='europe/moscow')

# %%
_, stps = pfs.as_positionfixes.generate_staypoints(method='sliding', time_threshold=0.2, dist_threshold=5)
ti.io.file.write_staypoints_csv(stps, '100000_stps.csv')

# %%
stps.as_staypoints.plot(out_filename='staypoints.png', radius=10, positionfixes=pfs, plot_osm=True)



# %%

# gdf_points.to_file('points_sample.json', driver="GeoJSON")