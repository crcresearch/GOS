import data
import numpy as np
import pandas as pd
import gc
from multiprocessing import Pool
import math
from constants import *

# df holds information on each country.
df = data.all()

# The attributes for each agent.
world_columns = ["Country", "Income", "Employed", "Attachment", "Location", "Migration"]

def max_value(attribute):
    """
    Get the maximum value for an attribute.
    """
    return df[attribute].max()

def neighbors(country):
    """
    Get the neighbors for a country.
    """
    return df[df.index == country].iloc[0].neighbors

def generate_agents(country, population):
    """
    Generate a dataframe of agents for a country where population
    is the number of agents to be created.
    """
    start = df[df.index < country].Population.sum()
    country_data = df[df.index == country].to_dict("records")[0]
    gdp = country_data["GDP"]
    income_array = gdp / 10 * np.random.chisquare(10, population).astype('float32')
    unemployment_rate = float(country_data["Unemployment"] / 100.0)
    employment_array = np.random.choice([True, False], population,
                                        p=[1 - unemployment_rate, unemployment_rate])
    attachment_array = (country_data["Fertility"] * np.random.triangular(0.0, 5.0, 10.0, population) / max_value("Fertility")).astype('float32')
    # Calculate migration likelyhood based on the numbers generated above
    # S1
    #conflict_score = pd.Series([10 * country_data["Conflict"] / max_value("Conflict")] * population).astype('float32')
    conflict_score = pd.Series([10 * np.log(1 + country_data["Conflict"]) / math.log(max_value("Conflict"))] * population).astype('float32')
    # S2
    income_score = income_array
    # TODO: What is the "brain drain" doing?
    #income_score.ix[income_score >= BRAIN_DRAIN_THRESHOLD * country_data["GDP"]] = country_data["GDP"]
    income_score /= -max_value("GDP")
    income_score += 1
    income_score *= 10
    unemployment_score = 7 - employment_array * 4
    frame =  pd.DataFrame({
        "Country": pd.Categorical([country] * population, list(df.index)),
        "Income": income_array,
        "Employed": employment_array.astype('bool'),
        "Attachment": attachment_array,
        "Location": pd.Categorical([country] * population, list(df.index)),
        "Migration": ((attachment_array + conflict_score + income_score + unemployment_score) / 37.0).astype('float32'),
    }, columns=world_columns)
    frame.index += start
    return frame

def create_agents(array):
    """
    Returns a dataframe with all agents in the model.
    """
    return pd.concat([generate_agents(country, len(population)) for country, population in array.groupby(array)])

country_array = pd.concat([pd.Series([c] * k["Population"]) for c, k in df.iterrows()])
country_array.index = range(len(country_array))
# Garbage collect before creating new processes.
gc.collect()
with Pool(THREADS) as p:
    world = pd.concat(p.map(create_agents, np.array_split(country_array, THREADS * SPLITS)))
    p.close()
    p.join()

world.Location = pd.Categorical(world["Location"], list(world[world.Migration > MIGRATION_THRESHOLD]["Country"].value_counts().index))

# Calculate attractiveness to migrants for each country.
attractiveness =  ((1 - df["Conflict"] / max_value("Conflict")) +
                   df["GDP"] / max_value("GDP") +
                   1 - df["Unemployment"] / max_value("Unemployment") +
                   1 - df["Fertility"] / max_value("Fertility"))

migration_map = {}
for country in df.index:
    local_attraction = attractiveness.copy()
    local_attraction[local_attraction.index.isin(neighbors(country))] += 1
    migration_map[country] = local_attraction

print("Migrating...")

def migrate_array(a):
    for country, population in a.groupby("Location"):
        local_attraction = migration_map[country]
        migrants = a[a.Migration > MIGRATION_THRESHOLD]
        a.loc[a.Migration > MIGRATION_THRESHOLD, "Location"] = df.sample(weights=local_attraction, n=len(migrants), replace=True).index
    return a

# Garbage collect before creating new processes.
gc.collect()
with Pool(THREADS) as p:
    world = pd.concat(p.map(migrate_array,
                            np.array_split(world,
                                           THREADS * SPLITS)))
    p.close()
    p.join()

print((world.Location.value_counts() - world.Country.value_counts()).sort_values())
