import matplotlib.pyplot as plt
import matplotlib.cm
import numpy as np
import pandas as pd
from mpl_toolkits.basemap import Basemap
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from matplotlib.colors import Normalize

def map(dataframe, title = "Map", colorbarName = None):

	fig, ax = plt.subplots(figsize=(80,40))

	m = Basemap(resolution='l', # c, l, i, h, f or None
		    projection='robin',
		    lon_0=0)

	m.drawmapboundary(fill_color='#46bcec')
	m.fillcontinents(color='#f2f2f2',lake_color='#46bcec')
	# m.drawcoastlines()

	plt.title(title, fontsize=50, y=1.08)

	m.readshapefile('visualization/World/World', 'world',drawbounds=False)

	df_plot = pd.DataFrame({
		'shapes': [Polygon(np.array(shape), True) for shape in m.world],
		'country': [country['ISO3'] for country in m.world_info]
	    })

	df_plot = df_plot.merge(dataframe, on='country', how='left')

	df_plot = df_plot.dropna()

	cmap = plt.get_cmap('RdYlGn')   
	pc = PatchCollection(df_plot.shapes, zorder=2)
	norm = Normalize()

	pc.set_facecolor(cmap(norm(df_plot['value'].values)))
	ax.add_collection(pc)

	mapper = matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap)

	mapper.set_array(df_plot['value'])
	cbar = plt.colorbar(mapper, shrink=0.7, label = colorbarName)
	

	fig = plt.gcf()
	fig.savefig("Map.jpg")

	plt.show()
