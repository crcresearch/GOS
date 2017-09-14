import sys
sys.path.append("visualization/")

#---Switch between two visualization methods by making one of the following lines as a comment---
import basemapviz as viz
#import plotlyviz as viz

import pandas as pd

COLUMNS = ["country", "value"]

#result = pd.read_csv('VizDemoData/changes.csv', names=COLUMNS)

result = pd.read_csv('VizDemoData/attractiveness.csv', names=COLUMNS)

#result = pd.read_csv('VizDemoData/migrants.csv', names=COLUMNS)

#---three arguments correspondingly are Pandas Dataframe, figure title, and colorbar label---
viz.map(result, "Country Attractiveness", "value")
