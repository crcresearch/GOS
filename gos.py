"""
The Global Open Simulator.
"""

import numpy as np
import pandas as pd
import gc
from multiprocessing import Pool, cpu_count
from functools import partial

class Globe:
    def __init__(self, df, threads=cpu_count() - 1, splits=1):
        self.df = df
        self.threads = threads
        self.splits = splits
        self.pool = Pool(self.threads)

    def __getstate__(self):
        self_dict = self.__dict__.copy()
        del self_dict['pool']
        return self_dict
    
    def max_value(self, attribute):
        """
        Returns the maximum value for an attribute.
        """
        return self.df[attribute].max()

    def _gen_agents(self, array):
        return pd.concat([self.generator(self.df, country, len(population)) for country, population in array.groupby(array)])

    def create_agents(self, generator):
        self.generator = generator
        country_array = pd.concat([pd.Series([c] * k["Population"]) for c, k in self.df.iterrows()])
        country_array.index = range(len(country_array))
        # Garbage collect before creating new processes.
        gc.collect()
        self.agents = pd.concat(self.pool.imap_unordered(self._gen_agents, np.array_split(country_array, self.threads * self.splits)))

    def run(self, function, **kwargs):
        # Garbage collect before creating new processes.
        gc.collect()
        self.agents = pd.concat(self.pool.imap_unordered(partial(function, **kwargs),
                                                         np.array_split(self.agents,
                                                                        self.threads * self.splits)))
