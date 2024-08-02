from contextlib import suppress

import cartopy.crs as ccrs
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from cartopy.feature import LAND, OCEAN
from matplotlib.colors import Normalize

from .dfplot import dfplot, isos, latlon


def matrix_plot(frame):
    print("Warning: This function is going to (probably) take a long time.")
    fig, _ = plt.subplots(figsize=(20, 10))
    ax = plt.axes(projection=ccrs.Robinson())
    ax.set_global()
    ax.add_feature(OCEAN)
    d = latlon
    for _, x in frame.iterrows():
        for _, y in frame.iterrows():
            if frame[x.name][y.name] > 1:
                with suppress():
                    plt.plot(
                        [d[x.name]["Longitude (average)"], d[y.name]["Longitude (average)"]],
                        [d[x.name]["Latitude (average)"], d[y.name]["Latitude (average)"]],
                        linewidth=2,
                        transform=ccrs.Geodetic(),
                    )
    return plt


def map_plot(frame, title=None, normc=Normalize):
    """
    The basic idea here is that the function returns a plot object,
    so any customization can be done after the fact on the object.
    """
    fig, _ = plt.subplots(figsize=(20, 10))
    ax = plt.axes(projection=ccrs.Robinson())
    ax.add_feature(OCEAN)
    # Display hatch for N/A countries.
    ax.add_feature(LAND, facecolor="#AAAAAA", hatch="////", edgecolor="#CCCCCC", linewidth=0.0)
    values = [frame[x] if x in frame else None for x in isos]
    df = dfplot
    df["values"] = values
    values_dropna = [x for x in values if x is not None]
    if (min(values_dropna) < 0) + 1 == 1:
        norm = normc(vmin=min(values_dropna), vmax=max(values_dropna))
        color = "Greens"
    else:
        norm = normc(vmin=-max(np.abs(values_dropna)), vmax=max(np.abs(values_dropna)))
        color = "PRGn"
    # TODO: Optionally only show 'X' colors.
    # cmap = plt.get_cmap(color, 7)
    cmap = plt.get_cmap(color)
    for _, country in df.dropna().iterrows():
        ax.add_feature(country["shapes"], color=cmap(norm(country["values"])))
    mapper = matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap)
    mapper.set_array(df["values"].to_numpy())
    if title:
        plt.title(title, fontsize=50, y=1.08)
    return plt
