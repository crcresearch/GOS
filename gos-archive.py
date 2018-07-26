import numpy as np
import pandas as pd
import gc
from multiprocessing import Pool, cpu_count
from functools import partial


class Globe:
    """
    Globe is used to store and process information about the word
    and an array of generated agents.
    """
    def __init__(self, df, processes=cpu_count() - 1, splits=1):
        """
        :param processes:
            The number of child processes to be created by the pool. Must be a
            minimum of one.
        :param splits:
            The number of subslices each process will be sent. For larger models
            this is needed because there is a limit to the size of data that can
            be sent between processes.
        """
        self.df = df
        self.processes = processes
        self.splits = splits
        self.pool = Pool(self.processes)

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
        return pd.concat(
            [self.generator(self.df, country, len(population))
             for country, population
             in array.groupby(array)]
        )

    def create_agents(self, generator):
        """
        Given information on a set of countries and a generator function,
        generate the agents and assign the results to ``self.agents``.

        :type generator: DataFrame, str, int
        :param generator: A function which generates the agents.
        """
        self.generator = generator
        country_array = pd.concat([pd.Series([c] * k["Population"]) for c, k in self.df.iterrows()])
        country_array.index = range(len(country_array))
        # Garbage collect before creating new processes.
        gc.collect()
        """
        self.agents = pd.concat(
            self.pool.imap(self._gen_agents,
                           np.array_split(country_array, self.processes * self.splits))
        )
        self.agents.index = range(len(self.agents))
        """
        self.agents = np.concatenate(
            self.pool.imap(self._gen_agents,
                           np.array_split(country_array, self.processes * self.splits))
        )

    def run_par(self, function, **kwargs):
        """
        Run a function on the agents in parallel.
        """
        columns = kwargs["columns"] if "columns" in kwargs else self.agents.columns
        # Garbage collect before creating new processes.
        gc.collect()
        return pd.concat(self.pool.imap(partial(function, **kwargs),
                                        np.array_split(self.agents[columns],
                                                       self.processes * self.splits)))
