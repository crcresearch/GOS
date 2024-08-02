import os

import cartopy.crs as ccrs
import pandas as pd
from cartopy.feature import ShapelyFeature
from cartopy.io.shapereader import Reader
from shapely.geometry.multipolygon import MultiPolygon


def get_df_plot():
    mod_dir, _ = os.path.split(__file__)
    shape_path = os.path.join(mod_dir, "World", "World.shp")
    countries = Reader(shape_path)
    shapes = []
    for geometry in countries.geometries():
        if type(geometry).__name__ == "Polygon":
            shapes.append(MultiPolygon([geometry]))
        else:
            shapes.append(geometry)
    df_plot = pd.DataFrame(
        {
            "shapes": [ShapelyFeature(x, ccrs.PlateCarree()) for x in shapes],
            "values": 0,
        }
    )
    isos = [x.attributes["ISO3"] for x in countries.records()]
    return df_plot, isos


dfplot, isos = get_df_plot()


def read_lat_lon():
    mod_dir, _ = os.path.split(__file__)
    data = pd.read_csv(
        os.path.join(mod_dir, "data", "Country_List_ISO_3166_Codes_Latitude_Longitude.csv"),
        usecols=[2, 4, 5],
        index_col=0,
    )
    return data.to_dict(orient="index")


latlon = read_lat_lon()
