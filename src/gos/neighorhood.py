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
            # elif item not in Neighborhood._names[key]:
            # for item in items:
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
            print("Could not find: ", missing)
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
