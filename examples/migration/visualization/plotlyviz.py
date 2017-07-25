import plotly
import pandas as pd

def map(dataframe):

	#plotly.offline.init_notebook_mode(connected=True)

	data = [ dict(
		type = 'choropleth',
		locations = dataframe['country'],
		z = dataframe['value'],
	#         text = dataframe['area'],
		colorscale = [[0,"rgb(215,25,28)"],[0.25,"rgb(253,174,97)"],[0.5,"rgb(255,255,191)"],[0.75,"rgb(166,217,106)"],[1,"rgb(26,150,65)"]],
		autocolorscale = False,
		reversescale = False,
		marker = dict(
		    line = dict (
		        color = 'rgb(180,180,180)',
		        width = 0.5
		    ) ),
		colorbar = dict(
		    autotick = False,
		    tickprefix = 'V',
		    title = 'Value<br>attractiveness'),
	      ) ]

	layout = dict(
	    title = 'Net Migration',
	    geo = dict(
		showframe = False,
		showcoastlines = False,
		projection = dict(
		    type = 'robin'
		)
	    )
	)

	fig = dict( data=data, layout=layout )
	#plotly.offline.iplot(fig, validate=False, filename='plotly-map' )
	plotly.offline.plot(fig, validate=False, filename='plotly-map' )
