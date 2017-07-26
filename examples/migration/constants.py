from multiprocessing import cpu_count

# The minimum size of a country (in population) to be added to the model.
MIN_POPULATION = 1900000

# Used to adjust the population.
# The population the model uses will be approximately the global population
# multiplied by POPULATION_SCALE.
POPULATION_SCALE = 1 / 1000

# Agents with a Migration score above this threshold will migrate.
MIGRATION_THRESHOLD = 0.7825

# Any income above this level multiplied by the country's GDP is brought
# down to this level.
BRAIN_DRAIN_THRESHOLD = 2.0

# The number of processes to spawn of in multiprocessing.
PROCESSES = cpu_count() - 1

# We need to pass pieces of the array to each process so it can do some work;
# however, pieces that are too large cannot be passed. SPLITS determines how
# arrays as subspliced to reduce their size.
SPLITS = int(100 * POPULATION_SCALE) if POPULATION_SCALE > 1 / 100 else 1
