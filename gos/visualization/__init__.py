# https://stackoverflow.com/questions/7404116/defining-the-midpoint-of-a-colormap-in-matplotlib
import numpy as np
from numpy import ma
import os
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import cbook
from matplotlib.colors import Normalize
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from matplotlib.colors import Normalize, LogNorm, BoundaryNorm

# This is a rewrite of the map_plot function using Cartopy
import cartopy.crs as ccrs
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature, OCEAN, LAND
from matplotlib.colors import Normalize
from matplotlib.collections import PatchCollection

COLOR1 = '#46bcec'
COLOR2 = '#eeeeee'

class MidPointNorm(Normalize):
    """
    Helper normalization class.
    """
    def __init__(self, midpoint=0, vmin=None, vmax=None, clip=False):
        Normalize.__init__(self,vmin, vmax, clip)
        self.midpoint = midpoint

    def __call__(self, value, clip=None):
        if clip is None:
            clip = self.clip

        result, is_scalar = self.process_value(value)

        self.autoscale_None(result)
        vmin, vmax, midpoint = self.vmin, self.vmax, self.midpoint

        if not (vmin < midpoint < vmax):
            raise ValueError("midpoint must be between maxvalue and minvalue.")       
        elif vmin == vmax:
            result.fill(0) # Or should it be all masked? Or 0.5?
        elif vmin > vmax:
            raise ValueError("maxvalue must be bigger than minvalue")
        else:
            vmin = float(vmin)
            vmax = float(vmax)
            if clip:
                mask = ma.getmask(result)
                result = ma.array(np.clip(result.filled(vmax), vmin, vmax),
                                  mask=mask)

            # ma division is very slow; we can take a shortcut
            resdat = result.data

            #First scale to -1 to 1 range, than to from 0 to 1.
            resdat -= midpoint            
            resdat[resdat>0] /= abs(vmax - midpoint)            
            resdat[resdat<0] /= abs(vmin - midpoint)

            resdat /= 2.
            resdat += 0.5
            result = ma.array(resdat, mask=result.mask, copy=False)                

        if is_scalar:
            result = result[0]            
        return result

    def inverse(self, value):
        if not self.scaled():
            raise ValueError("Not invertible until scaled")
        vmin, vmax, midpoint = self.vmin, self.vmax, self.midpoint

        if cbook.iterable(value):
            val = ma.asarray(value)
            val = 2 * (val-0.5)  
            val[val>0]  *= abs(vmax - midpoint)
            val[val<0] *= abs(vmin - midpoint)
            val += midpoint
            return val
        else:
            val = 2 * (val - 0.5)
            if val < 0: 
                return  val*abs(vmin-midpoint) + midpoint
            else:
                return  val*abs(vmax-midpoint) + midpoint

mod_dir, filename = os.path.split(__file__)
shape_path = os.path.join(mod_dir, "World")
countries = Reader(shape_path)
isos = [x.attributes['ISO3'] for x in countries.records()]
df_plot = pd.DataFrame({
    #'shapes': [ShapelyFeature(x, ccrs.PlateCarree()) for x in countries.geometries()],
    'country': isos,
    'values': 0,
})

def map_plot(title, color, data, normc, sides=1):
    fig, _ = plt.subplots(figsize=(20, 10))
    ax = plt.axes(projection=ccrs.Robinson())
    ax.add_feature(OCEAN)
    ax.add_feature(LAND, facecolor='none', hatch='////', edgecolor='#CCCCCC',linewidth=0.0)
    values = [data[x] if x in data else None for x in isos]
    df = df_plot
    df["values"] = values
    values = data.values
    # TODO: This needs to be adjusted based on sides
    #norm = normc(vmin=min(values), vmax=max(values))
    if sides == 1:
        norm = normc(
            vmin=min(values),
            vmax=max(values))
    else:
        norm = normc(
            vmin=-np.max(np.abs(values)),
            vmax=np.max(np.abs(values)))
    cmap = plt.get_cmap(color, 7)
    for _, country in df.dropna().iterrows():
        ax.add_feature(country["shapes"], color=cmap(norm(country["values"])))
    mapper = matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap)
    mapper.set_array(df['values'])
    cbar = plt.colorbar(mapper, shrink=0.7,
                        orientation='horizontal')
    plt.title(title, fontsize=50, y=1.08)
    fig = plt.gcf()
    return plt

COLOR1 = '#333333'
COLOR2 = '#000000'

# TODO: This doesn't work quite yet.
def plot_lines(matrix, distance_frame):
    fix, ax = plt.subplots(figsize=(24, 12))
    
    ax = plt.axes(projection=ccrs.Robinson())
    ax.set_global()
    ax.add_feature(OCEAN, color=COLOR2)
    ax.add_feature(LAND, color=COLOR1)
    d = distance_frame[distance_frame.index.isin(world.data.index)]
    for _, x in d.iterrows():
        for _, y in d.iterrows():
            if matrix[x.name][y.name] > 0.1:
                 plt.plot(
                        [x["Longitude (average)"],
                        x["Latitude (average)"]],
                        [y["Longitude (average)"],
                        y["Latitude (average)"]],
                        linewidth=2,
                        color='#00FF00{:02X}'.format((int(25 + 100 * matrix[x.name][y.name] / matrix.max().max()))),
                        transform=ccrs.PlateCarree()
                    )
    fig = plt.gcf()
    return fig
