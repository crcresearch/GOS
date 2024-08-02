from multiprocessing import Pool

import pandas as pd

from gos import Neighborhood


class World:
    """
    World is used to store and process information about the word
    and an array of generated agents.
    """

    def __init__(self, processes=1, index=[]):
        self._index = set(index)
        self.data = pd.DataFrame(index=index)
        self.matrices: dict[str, pd.DataFrame] = {}  # pd.DataFrame(index=index, columns=index)
        self.processes = processes
        # TODO: Assert this is greater than or equal to one.
        if self.processes > 1:
            self.pool = Pool(self.processes)

    def __getstate__(self):
        # TODO: Document why this function is needed.
        # I honestly forgot. Probably something to do
        # with multiprocessing.
        self_dict = self.__dict__.copy()
        del self_dict["pool"]
        return self_dict

    def update_neighborhoods(self, df, name=None):
        df.index = Neighborhood.translate(df.index)
        missing_in = [x for x in df.index if x not in self._index]
        missing_out = [x for x in self._index if x not in df.index]
        print("Dropped: ", missing_in)
        print("Not found in other sets: ", missing_out)
        self._index -= set(missing_out)
        if name is None:
            self.data = self.data.join(df, how="inner")
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
