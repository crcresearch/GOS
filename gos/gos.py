import numpy as np
import pandas as pd
from multiprocessing import Pool

class Neighborhood:
    _names = {}
    _namemap = {}
    # We don't expect for there to be a large quantity of Neighborhoods.
    # Therefore, this class isn't designed with efficiency in mind
    # per se.
    def __init__(self):
        pass

    @staticmethod
    def update(dictionary: dict):
        for key, items in dictionary.items():
            if key not in Neighborhood._names:
                # TODO: It may be necessary to check if `item`
                # is unique for `_get_name_map()` to function
                # properly.
                Neighborhood._names[key] = set()
            #elif item not in Neighborhood._names[key]:
            #for item in items:
            Neighborhood._names[key] |= set(items)
        Neighborhood._namemap = Neighborhood._get_name_map()

    @staticmethod
    def _get_name_map():
        d = {}
        for key, items in Neighborhood._names.items():
            for item in items:
                d[item] = key
            d[key] = key
        return d

    @staticmethod
    def translate(series):
        # TODO: Reimlement the `missing` functionaility here.
        missing = [x for x in series if x not in Neighborhood._namemap]
        if len(missing) > 0:
            print(
                "Could not find: ",
                missing
            )
        return [Neighborhood._namemap[x] if x in Neighborhood._namemap else None for x in series]

    @staticmethod
    def translate_matrix(matrix):
        matrix.index = Neighborhood.translate(matrix.index)
        matrix.columns = Neighborhood.translate(matrix.columns)
        if None in matrix.index:
            matrix = matrix.drop([None])
        if None in matrix.columns:
            matrix = matrix.drop([None], axis=1)
        return matrix

class World:
    """
    World is used to store and process information about the word
    and an array of generated agents.
    """
    def __init__(self, processes=1, index=[]):
        self._index = set(index)
        self.data = pd.DataFrame(index=index)
        self.matrices = {}#pd.DataFrame(index=index, columns=index)
        self.processes = processes
        # TODO: Assert this is greater than or equal to one.
        if self.processes > 1:
            self.pool = Pool(self.processes)

    def __getstate__(self):
        # TODO: Document why this function is needed.
        # I honestly forgot. Probably something to do
        # with multiprocessing.
        self_dict = self.__dict__.copy()
        del self_dict['pool']
        return self_dict

    def update_neighborhoods(self, df, name=None):
        df.index = Neighborhood.translate(df.index)
        missing_in = [x for x in df.index if x not in self._index]
        missing_out = [x for x in self._index if x not in df.index]
        print("Dropped: ", missing_in)
        print("Not found in other sets: ", missing_out)
        self._index -= set(missing_out)
        if name is None:
            self.data = self.data.join(df, how='inner')
            self._drop_missing()
            return self.data[df.columns]
        else:
            series = df
            self.data[name] = series
            self._drop_missing()
            return self.data[name]

    def add_matrix(self, name, matrix):
        self.matrices[name] = Neighborhood.translate_matrix(matrix)
        self._drop_missing()
        return self.matrices[name]

    def _drop_missing(self):
        intersection = self._index & set(self.data.index)
        for s in [set(x.index) for _, x in self.matrices.items()]:
            intersection &= s
        # TODO: Collect a set of the intersection between the main dataset
        # and the matrix. Then drop anything which isn't in that intersection.
        for key, value in self.matrices.items():
            drop = [x for x in value.index if x not in intersection]
            v = value.drop(drop)
            drop = [x for x in value.columns if x not in intersection]
            v = v.drop(drop, axis=1)
            self.matrices[key] = v
        self.data = self.data[self.data.index.isin(intersection)]
        self._index = intersection

class Agent:
    # TODO: This will be a pretty important class later on,
    # but is a little outside of the scope of my work on the
    # migration model this summer.
    pass


# TODO: Consider some other important steps in the process
# of developing agent-based models:
# - Validation
# - ????
