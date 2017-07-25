import numpy as np
import pandas as pd
import data as data
from constants import POPULATION_SCALE, MIGRATION_THRESHOLD, PROCESSES, SPLITS
from gos import Globe

# The attributes for each agent.
world_columns = ["Country", "Income", "Employed", "Attachment", "Location", "Migration"]


def generate_agents(df, country, population):
    """
    Generate a dataframe of agents for a country where population
    is the number of agents to be created.
    """
    def max_value(attribute):
        return df[attribute].max()
    # Turn this on for truly random output from each process.
    # pid = mp.current_process()._identity[0]
    rand = np.random.mtrand.RandomState(0)
    country_data = df[df.index == country].to_dict("records")[0]
    gdp = country_data["GDP"]
    income_array = gdp / 10 * rand.chisquare(10, population).astype('float32')
    unemployment_rate = float(country_data["Unemployment"] / 100.0)
    employment_array = rand.choice([True, False], population,
                                   p=[1 - unemployment_rate, unemployment_rate])
    attachment_array = (country_data["Fertility"] *
                        rand.triangular(0.0, 0.5, 1.0, population) /
                        max_value("Fertility")).astype('float32')
    frame = pd.DataFrame({
        "Country": pd.Categorical([country] * population, list(df.index)),
        "Income": income_array,
        "Employed": employment_array.astype('bool'),
        "Attachment": attachment_array,
        "Location": pd.Categorical([country] * population, list(df.index)),
        "Migration": 0,
    }, columns=world_columns)
    return frame


def migrate_array(a, **kwargs):
    if len(a[a.Migration > MIGRATION_THRESHOLD]) == 0:
        return a.Location
    np.random.seed(1000)
    migration_map = kwargs["migration_map"]
    countries = kwargs["countries"]
    for country, population in a.groupby("Location"):
        local_attraction = migration_map[country]
        local_attraction /= local_attraction.sum()
        migrants_num = len(population[population.Migration > MIGRATION_THRESHOLD])
        a.loc[(a.Country == country) & (a.Migration > MIGRATION_THRESHOLD),
              "Location"] = np.random.choice(countries,
                                             p=local_attraction,
                                             size=migrants_num,
                                             replace=True)
    return a.Location


def migrate_score(a, **kwargs):
    max_income = kwargs["max_income"]
    conflict_scores = kwargs["conflict"]
    max_conflict = kwargs["max_conflict"]
    conflict = conflict_scores.merge(a, left_index=True,
                                     right_on='Location')["Conflict"] / max_conflict
    return ((10 * (1 + a.Income / -max_income) +
             10 * a.Attachment +
             (5 * conflict) +
             3 + a.Employed * 4) / 32).astype('float32')


def main():
    np.random.seed(1000)
    globe = Globe(data.all(), processes=PROCESSES, splits=SPLITS)

    globe.create_agents(generate_agents)

    globe.agents.Migration = globe.run_par(migrate_score, max_income=globe.agents.Income.max(),
                                           conflict=globe.df[["Conflict"]].sort_index(),
                                           max_conflict=globe.df.Conflict.max(),
                                           columns=["Income", "Employed", "Attachment", "Location"])

    attractiveness = ((1 - globe.df["Conflict"] / globe.max_value("Conflict")) +
                      (globe.df["GDP"] / globe.max_value("GDP")) +
                      (1 - globe.df["Unemployment"] / globe.max_value("Unemployment")) +
                      (1 - globe.df["Fertility"] / globe.max_value("Fertility")))

    attractiveness.to_csv('attractiveness.csv')

    def neighbors(country):
        return globe.df[globe.df.index == country].iloc[0].neighbors

    migration_map = {}
    for country in globe.df.index:
        local_attraction = attractiveness.copy()
        local_attraction[local_attraction.index.isin(neighbors(country))] += 1
        migration_map[country] = local_attraction

    globe.agents["Location"] = globe.run_par(migrate_array, migration_map=migration_map,
                                             countries=globe.df.index,
                                             columns=["Country", "Location", "Migration"])

    print("Migration model completed at a scale of {}:1.".format(int(1 / POPULATION_SCALE)))
    migrants = globe.agents[globe.agents.Country != globe.agents.Location]
    print("There were a total of {} migrants.".format(len(migrants)))
    print("There were a total of {} agents.".format(len(globe.agents)))
    changes = (globe.agents.Location.value_counts() -
               globe.agents.Country.value_counts()).sort_values()
    changes.to_csv('changes.csv')
    print(changes.head())
    print(changes.tail())
    print("The potential migrants came from")
    migrants = globe.agents[globe.agents.Migration > MIGRATION_THRESHOLD]
    ms = migrants.Country.value_counts()
    ms2 = migrants.Country.value_counts()[migrants.Country.value_counts().gt(0)]
    ms.to_csv('ms.csv')
    ms2.to_csv('ms2.csv')
    print(migrants.Country.value_counts()[migrants.Country.value_counts().gt(0)])
    return globe


if __name__ == "__main__":
    main()
