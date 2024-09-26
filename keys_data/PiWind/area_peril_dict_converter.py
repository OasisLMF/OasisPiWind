from shapely.geometry import Polygon
import geopandas as gpd
import pandas as pd
import os

df = pd.read_csv(os.path.join(os.path.dirname(__file__), "areaperil_dict.csv"))
df.rename(columns={column:column.lower() for column in df.columns}, inplace=True)

polygon_point_order = [1, 2, 4, 3]

# create the GeoDataFrame and its geometry
gdf_peril_area = gpd.GeoDataFrame(df)
gdf_peril_area["geometry"] = gdf_peril_area.apply(
    lambda row: Polygon([(row[f"lon{i}"], row[f"lat{i}"]) for i in polygon_point_order]), axis=1)

# remove unused coordinate
gdf_peril_area.drop(columns=sum(([f"lon{i}", f"lat{i}"] for i in polygon_point_order), []), inplace=True)

# store to parquet format
gdf_peril_area.to_parquet(os.path.join(os.path.dirname(__file__), "areaperil_dict.parquet"))
