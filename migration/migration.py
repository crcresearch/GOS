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

def migrate_array(a, **kwargs):
    migration_map = kwargs["migration_map"]
    countries = kwargs["countries"]
    for country, population in a.groupby("Location"):
        local_attraction = migration_map[country]
        local_attraction /= local_attraction.sum()
        migrants = a[a.Migration > MIGRATION_THRESHOLD]
        a.loc[a.Migration > MIGRATION_THRESHOLD, "Location"] = np.random.choice(countries, p=local_attraction, size=len(migrants), replace=True)
    return a


def main():
    globe = gos.Globe(data.all(), threads=THREADS, splits=SPLITS)

    globe.create_agents(generate_agents)

    attractiveness = ((1 - globe.df["Conflict"] / globe.max_value("Conflict")) +
                      globe.df["GDP"] / globe.max_value("GDP") +
                      1 - globe.df["Unemployment"] / globe.max_value("Unemployment") +
                      1 - globe.df["Fertility"] / globe.max_value("Fertility"))

    def neighbors(country):
        """
        Get the neighbors for a country.
        """
        return globe.df[globe.df.index == country].iloc[0].neighbors

    migration_map = {}
    for country in globe.df.index:
        local_attraction = attractiveness.copy()
        local_attraction[local_attraction.index.isin(neighbors(country))] += 1
        migration_map[country] = local_attraction

    globe.run(migrate_array, migration_map=migration_map, countries=globe.df.index)

    print((globe.agents.Location.value_counts() - globe.agents.Country.value_counts()).sort_values())
    return globe

if __name__ == "__main__":
    main()
