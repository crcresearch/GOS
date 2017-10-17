import numpy as np
import sharedmem
import data as data
import pandas as pd
from gos import Globe
from constants import POPULATION_SCALE, MIGRATION_THRESHOLD, PROCESSES, SPLITS, BRAIN_DRAIN_THRESHOLD

agentdt = np.dtype([('country', np.uint8),
                    ('income', np.float16),
                    ('high income', np.bool),
                    ('employed', np.bool),
                    ('attachment', np.float16),
                    ('location', np.uint8),
                    ('neighborhood', np.uint8),
                    ('migration', np.float32)])

globe = Globe(data.all())
globe.df.Population.sum()
countries = globe.df.as_matrix()
population = globe.df.Population.sum()
attractiveness = ((1 - countries[:,3] / np.max(countries[:,3])) +
                  countries[:,1] / np.max(countries[:,1]) +
                  (1 - countries[:,2] / np.max(countries[:,2])) +
                  (1 - countries[:,4] / np.max(countries[:,4]))).astype(np.float32)


agents = sharedmem.empty(globe.df.Population.sum(), dtype=agentdt)
agents["country"] = np.concatenate([np.full(countries[x][0], x) for x in range(0, len(countries))])
with sharedmem.MapReduce() as pool:
    chunksize = 1024 * 16
    def gen_agents(i):
        s = slice(i, i + chunksize)
        agents[s]["location"] = agents[s]["country"]
        agents[s]["income"] = countries[agents[s]['country'],1] * np.random.chisquare(10, len(agents[s])).astype('float32') / 10
        agents[s]["high income"] = agents[s]["income"] > BRAIN_DRAIN_THRESHOLD * countries[agents[s]['country'],1]
        agents[s]["employed"] = countries[agents[s]['country'],2] / 100 > np.random.rand(len(agents[s]))
        agents[s]["attachment"] = countries[agents[s]['country'],4] * np.random.triangular(0.0, 0.5, 1.0, len(agents[s])) / np.max(countries[:,4])
        agents[s]["migration"] = (10 * (1 + agents[s]["income"] / -agents[s]["income"].max()) +
                                  10 * agents[s]["attachment"] +
                                  5 * countries[agents[s]['country'],3] / np.max(countries[:,3]) +
                                  7 - 4 * agents[s]["employed"]) / 32
    def migrate(i):
        s = slice(i, i + chunksize)
        for x in np.nditer(agents[s], op_flags=['readwrite']):
            if x["migration"] > MIGRATION_THRESHOLD:
                 x["location"] = np.random.choice(len(countries), p=attractiveness / np.sum(attractiveness))
    pool.map(gen_agents, range(0, len(agents), chunksize))
    pool.map(migrate, range(0, len(agents), chunksize))
"""
agents["country"] = np.concatenate([np.full(countries[x][0], x) for x in range(0, len(countries))])
agents["location"] = agents["country"]
agents["income"] = countries[agents['country'],1] * np.random.chisquare(10, population).astype('float32') / 10
agents["high income"] = agents["income"] > BRAIN_DRAIN_THRESHOLD * countries[agents['country'],1]
agents["employed"] = countries[agents['country'],2] / 100 > np.random.rand(len(agents))
agents["attachment"] = countries[agents['country'],4]
agents["attachment"] /= agents["attachment"].max()
agents["attachment"] *= np.random.triangular(0.0, 0.5, 1.0, len(agents))
agents["migration"] = (10 * (1 + agents["income"] / -agents["income"].max()) +
                       10 * agents["attachment"] +
                       5 * countries[agents['country'],3] / np.max(countries[agents['country'],3]) +
                       7 - 4 * agents["employed"]) / 32
"""
 #= np.random.choice(len(countries), size=num, p=attractiveness / np.sum(attractiveness))
#print(agents)
#print(len(agents[agents['country'] != agents['location']]))
#print(agents[['migration','location']])
#print(agents[agents["migration"] > MIGRATION_THRESHOLD])
#print(agents[agents["migration"] > MIGRATION_THRESHOLD]['location'])
