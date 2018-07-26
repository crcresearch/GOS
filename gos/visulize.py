# https://stackoverflow.com/questions/7404116/defining-the-midpoint-of-a-colormap-in-matplotlib
import numpy as np
from numpy import ma
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import cbook
from matplotlib.colors import Normalize
from matplotlib.patches import Polygon
from mpl_toolkits.basemap import Basemap
from matplotlib.collections import PatchCollection
from matplotlib.colors import Normalize, LogNorm, BoundaryNorm

COLOR1 = '#46bcec'
COLOR2 = '#eeeeee'

class MidPointNorm(Normalize):    
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

def map_plot(title, color, data, normc, sides=1):
    fix, ax = plt.subplots(figsize=(20, 10))
    m = Basemap(resolution='l',
               projection='robin',
               lon_0=0)

    m.drawmapboundary(fill_color=COLOR1)
    m.fillcontinents(color='#FFFFFF', lake_color=COLOR1)
    plt.title(title, fontsize=50, y=1.08)
    m.readshapefile('./gos/World/World', 'world',drawbounds=False)
    l = [country['ISO3'] for country in m.world_info]
    df_plot = pd.DataFrame({
        'shapes': [Polygon(np.array(shape), True) for shape in m.world],
        'country': l,
        'values': [data[x] if x in data else None for x in l]
    })
    df_plot = df_plot.dropna()

    cmap = plt.get_cmap(color, 7)
    pc = PatchCollection(df_plot.shapes, zorder=2)
    if sides == 1:
        norm = normc(
            vmin=df_plot['values'].min(),
            vmax=df_plot['values'].max())
    else:
        norm = normc(
            vmin=-df_plot['values'].abs().max(),
            vmax=df_plot['values'].abs().max())
    pc.set_facecolor(cmap(norm(df_plot['values'].values)))
    ax.add_collection(pc)

    mapper = matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap)
    mapper.set_array(df_plot['values'])
    cbar = plt.colorbar(mapper, shrink=0.7,
                       orientation='horizontal')

    fig = plt.gcf()

    return plt

"""
def plot_lines(matrix):
    fix, ax = plt.subplots(figsize=(24, 12))
    m = Basemap(resolution='l',
               projection='robin',
               lon_0=0)

    m.drawmapboundary(fill_color=COLOR1)
    m.fillcontinents(color=COLOR2, lake_color=COLOR1)
    d = distance_frame[distance_frame.index.isin(world.data.index)]
    for _, x in d.iterrows():
        for _, y in d.iterrows():
            if matrix[x.name][y.name] > 0.1:
                m.drawgreatcircle(
                    x["Longitude (average)"],
                    x["Latitude (average)"],
                    y["Longitude (average)"],
                    y["Latitude (average)"],
                    linewidth=2, #5 * (matrix[x.name][y.name] / matrix.max().max()) + 2,
                    color='#00FF00{:02X}'.format((int(25 + 100 * matrix[x.name][y.name] / matrix.max().max())))
                )
    return plt
"""
