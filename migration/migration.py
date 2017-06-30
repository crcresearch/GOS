import sys
import data
sys.path.append("..")
import gos
import numpy as np
import pandas as pd
import math
from constants import *

# The attributes for each agent.
world_columns = ["Country", "Income", "Employed", "Attachment", "Location", "Migration"]

def generate_agents(df, country, population):
    """
    Generate a dataframe of agents for a country where population
    is the number of agents to be created.
    """
    def max_value(attribute):
        return df[attribute].max()

    start = df[df.index < country].Population.sum()
    country_data = df[df.index == country].to_dict("records")[0]
    gdp = country_data["GDP"]
    income_array = gdp / 10 * np.random.chisquare(10, population).astype('float32')
    unemployment_rate = float(country_data["Unemployment"] / 100.0)
    employment_array = np.random.choice([True, False], population,
                                    p=[1 - unemployment_rate, unemployment_rate])
    attachment_array = (country_data["Fertility"] * np.random.triangular(0.0, 0.5, 1.0, population) / max_value("Fertility")).astype('float32')
    frame =  pd.DataFrame({
        "Country": pd.Categorical([country] * population, list(df.index)),
        "Income": income_array,
        "Employed": employment_array.astype('bool'),
        "Attachment": attachment_array,
        "Location": pd.Categorical([country] * population, list(df.index)),
        "Migration": 0,
    }, columns=world_columns)
    frame.index += start
    return frame

def migrate_array(a, **kwargs):
    if len(a[a.Migration > MIGRATION_THRESHOLD]) == 0:
        return a
    migration_map = kwargs["migration_map"]
    countries = kwargs["countries"]
    for country, population in a.groupby("Location"):
        local_attraction = migration_map[country]
        local_attraction /= local_attraction.sum()
        migrants_num = len(population[population.Migration > MIGRATION_THRESHOLD])
        a.loc[(a.Country == country) & (a.Migration > MIGRATION_THRESHOLD), "Location"] = np.random.choice(countries, p=local_attraction, size=migrants_num, replace=True)
    return a

def migrate_score(income, attachment, employed, conflict):
    return np.array(((10 * (1 + income / -np.max(income)) +
                      10 * attachment +
                      (5 * conflict / np.max(conflict)) +
                      3 + employed * 4)
                     / 32), dtype='float32')

def main():
    globe = gos.Globe(data.all(), threads=THREADS, splits=SPLITS)

    globe.create_agents(generate_agents)

    conflict_values = globe.df[["Conflict"]].merge(globe.agents, left_index=True, right_on='Country')["Conflict"].values
    globe.agents.Migration = migrate_score(globe.agents.Income.values, globe.agents.Attachment.values, globe.agents.Employed.values, conflict_values)

    attractiveness = ((1 - globe.df["Conflict"] / globe.max_value("Conflict")) +
                      (globe.df["GDP"] / globe.max_value("GDP")) +
                      (1 - globe.df["Unemployment"] / globe.max_value("Unemployment")) +
                      (1 - globe.df["Fertility"] / globe.max_value("Fertility")))

    def neighbors(country):
        return globe.df[globe.df.index == country].iloc[0].neighbors

    migration_map = {}
    for country in globe.df.index:
        local_attraction = attractiveness.copy()
        local_attraction[local_attraction.index.isin(neighbors(country))] += 1
        migration_map[country] = local_attraction

    globe.run(migrate_array, migration_map=migration_map, countries=globe.df.index)

    print("Migration model completed at a scale of {}:1.".format(int(1 / POPULATION_SCALE)))
    migrants = globe.agents[globe.agents.Country != globe.agents.Location]
    print("There were a total of {} migrants.".format(len(migrants)))
    changes = (globe.agents.Location.value_counts() - globe.agents.Country.value_counts()).sort_values()
    print(changes.head())
    print(changes.tail())
    
    print("The potential migrants came from")
    migrants = globe.agents[globe.agents.Migration > MIGRATION_THRESHOLD]
    print(migrants.Country.value_counts()[migrants.Country.value_counts().gt(0)])
    return globe

if __name__ == "__main__":
    main()
