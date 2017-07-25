import sys
sys.path.append("visualization/")
import plotlyviz as viz
import pandas as pd

COLUMNS = ["country", "value"]

result = pd.read_csv('changes.csv', names=COLUMNS)

#result = pd.read_csv('attractiveness.csv', names=COLUMNS)

#result = pd.read_csv('ms2.csv', names=COLUMNS)

viz.map(result)
