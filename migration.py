import csv
import numpy as np
import pandas as pd
import time
import gc
from multiprocessing import Pool

# The minimum size of a country (in population) to be added to the model.
MIN_POPULATION = 1900000
# Used to adjust the population.
# The population the model uses will be approximately the global population
# multiplied by POPULATION_SCALE.
POPULATION_SCALE = 1 / 1000
# Agents with a Migration score above this threshold will migrate.
MIGRATION_THRESHOLD = 0.75
# Any income above this level multiplied by the country's GDP is brought
# down to this level.
BRAIN_DRAIN_THRESHOLD = 1.5
# The number of processes to spawn of in multiprocessing.
THREADS = 8
# We need to pass pieces of the array to each process so it can do some work;
# however, pieces that are too large cannot be passed. SPLITS determines how
# arrays as subspliced to reduce their size.
SPLITS = int(1000 * POPULATION_SCALE) if POPULATION_SCALE > 1 / 1000 else 1

# A dictionary with entries for each country.
countries = {}

def csv_path(name):
    """
    Shortcut function to get the relative path to the directory
    which contains the CSV data.
    """
    return "test_model/CountryData/CSVfiles/%s" % name

## TODO: The process of reading in this data is rather similar for each
## set of data. Would it be possible to create a function which simplifies
## this an reduces the amount of redundancy?

# Read population data.
with open(csv_path("Population.csv")) as fh:
    reader = csv.DictReader(fh)
    for entry in reader:
        pop = int((entry["Population"]).replace(",",""))
        if pop > MIN_POPULATION:
            countries[entry["Country"]] = {}
            countries[entry["Country"]]["Population"] = int(pop * POPULATION_SCALE)

# Read GDP data.
with open(csv_path("UN_GDP.csv")) as fh:
    reader = csv.DictReader(fh)
    for entry in reader:
        country = entry["Country"]
        if country in countries:
            countries[country]["GDP"] = float(entry["Value"])

# Read unemployment data
with open(csv_path("CIA_Unemployment.csv")) as fh:
    reader = csv.DictReader(fh)
    for entry in reader:
        country = entry["Country"]
        if country in countries:
            countries[country]["Unemployment"] = float(entry["Unemployment"])

iso_codes = {}
# Read ISO codes
with open(csv_path("Neighbors.csv")) as fh:
    reader = csv.DictReader(fh)
    for entry in reader:
        iso_codes[entry["iso_alpha2"]] = entry["Country"]
# Find neighbors for each country.
with open(csv_path("Neighbors.csv")) as fh:
    reader = csv.DictReader(fh)
    for entry in reader:
        country = entry["Country"]
        neighbors = entry["neighbors"].split()
        if country in countries:
            countries[country]["Neighbors"] = []
            for abbr in neighbors:
                countries[country]["Neighbors"].append(iso_codes[abbr])
# Island nations are a weird exceptions
countries["Madagascar"]["Neighbors"] = ["Mozambique", "South Africa", "Tanzania"]
countries["Taiwan"]["Neighbors"] = ["China", "Philippines"]
countries["New Zealand"]["Neighbors"] = ["Australia"]
countries["Japan"]["Neighbors"] = ["Taiwan", "South Korea", "Philippines"]
# TODO: Why isn't Norway getting any neighbors?
countries["Norway"]["Neighbors"] = ["Sweden"]
countries["Singapore"]["Neighbors"] = ["Malaysia", "Indonesia"]
countries["Puerto Rico"]["Neighbors"] = ["United States", "Dominican Republic"]
countries["Jamaica"]["Neighbors"] = ["Cuba", "Dominican Republic"]

# Get attachment scores for each country (fertility).
with open(csv_path("attachment.csv")) as fh:
    reader = csv.DictReader(fh)
    for entry in reader:
        score = float(entry["Total fertility rate"])
        country = entry["Country"].split(',')[0]
        if country in countries:
            countries[country]["Fertility"] = score

# Calculate "Conflict" scores.
with open(csv_path("Mainconflicttable.csv")) as fh:
    reader = csv.DictReader(fh)
    for entry in reader:
        #score = ((int(entry['YEAR']) - 1946) / 10) * (int(entry['Intensity'])**2)
        score = (int(entry['Intensity'])**2)
        for country in entry['Country'].split(','):
            country = country.strip()
            if country == 'Russia (Soviet Union)':
                country = 'Russia'
            elif country == 'Hyderabad':
                country = 'India'
            elif 'Yemen' in country:
                country = 'Yemen'
            elif country == 'United States of America':
                country = 'United States'
            elif 'Vietnam' in country:
                country = 'Vietnam'
            elif country == 'Democratic Republic of Congo (Zaire)':
                country = 'Democratic Republic of the Congo'
            elif country == 'Guinea-Bissau':
                country = 'Guinea'
            elif country == 'Sri Lanka (Ceylon)':
                country = 'Sri Lanka'
            elif country == 'Zimbabwe (Rhodesia)':
                country = 'Zimbabwe'
            elif country == 'Turkey/Ottoman Empire':
                country = 'Turkey'
            elif country == 'Yugoslavia (Serbia)':
                country = 'Serbia'
            elif country == 'Cote DÕIvoire':
                country = "Cote d'Ivoire"
            elif country == 'Rumania':
                country = 'Romania'
            if country in countries:
                if not "Conflict" in countries[country]:
                    countries[country]["Conflict"] = score
                else:
                    countries[country]["Conflict"] += score

# At this point, all data has been imported and is currently stored in a dictionary.
# We will now convert that data into a pandas dataframe.
df = pd.DataFrame(countries).transpose().sort_values(["Population"], ascending=False)
df[["Population"]] = df[["Population"]].apply(pd.to_numeric, downcast="unsigned")
df[["Conflict", "Fertility", "GDP", "Unemployment"]] = df[["Conflict", "Fertility", "GDP", "Unemployment"]].apply(pd.to_numeric, downcast="float")

# Some countries are missing data. We will guess this data using that of
# neighboring countries.
for i in range(2):
    # Fill in unemployment data
    for item, frame in df[df.Unemployment.isnull()]["Neighbors"].iteritems():
        df.set_value(item, "Unemployment", df[df.index.isin(frame)]["Unemployment"].mean())
    # Fill in conflict data
    for item, frame in df[df.Conflict.isnull()]["Neighbors"].iteritems():
        df.set_value(item, "Conflict", df[df.index.isin(frame)]["Conflict"].mean())
    # Fill in fertility data
    for item, frame in df[df.Fertility.isnull()]["Neighbors"].iteritems():
        df.set_value(item, "Fertility", df[df.index.isin(frame)]["Fertility"].mean())
    # Fill in GDP data
    for item, frame in df[df.GDP.isnull()]["Neighbors"].iteritems():
        df.set_value(item, "GDP", df[df.index.isin(frame)]["GDP"].mean())

# Now we will generate our agents.
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
    return df[df.index == country].iloc[0].Neighbors

def generate_agents(country, population):
    """
    Generate a dataframe of agents for a country where population
    is the number of agents to be created.
    """
    start = df[df.index < country].Population.sum()
    country_data = df[df.index == country].to_dict("records")[0]
    gdp = country_data["GDP"]
    income_array = np.random.triangular(0.0, 0.75 * gdp, 2.5 * gdp, population).astype('float32')
    unemployment_rate = float(country_data["Unemployment"] / 100.0)
    employment_array = np.random.choice([True, False], population,
                                        p=[1 - unemployment_rate, unemployment_rate])
    attachment_array = (country_data["Fertility"] * np.random.triangular(0.0, 5.0, 10.0, population) / max_value("Fertility")).astype('float32')
    # Calculate migration likelyhood based on the numbers generated above
    # S1
    conflict_score = pd.Series([10 * country_data["Conflict"] / max_value("Conflict")] * population).astype('float32')
    # S2
    income_score = pd.Series(income_array)
    income_score.ix[income_score >= BRAIN_DRAIN_THRESHOLD * country_data["GDP"]] = country_data["GDP"]
    income_score /= max_value("GDP")
    income_score *= -1
    income_score += 1
    income_score *= 10
    unemployment_score = 7 - employment_array * 4
    frame =  pd.DataFrame({
        "Country": pd.Categorical([country] * population, list(countries)),
        "Income": income_array,
        "Employed": employment_array.astype('bool'),
        "Attachment": attachment_array,
        "Location": [country] * population,
        "Migration": ((attachment_array + conflict_score + income_score + unemployment_score) / 37.0).astype('float32'),
    }, columns=world_columns)
    frame.index += start
    return frame

def create_agents(array):
    """
    Returns a dataframe with all agents in the model.
    """
    return pd.concat([generate_agents(country, len(population)) for country, population in array.groupby(array)])

country_array = pd.concat([pd.Series([c] * k["Population"]) for c, k in countries.items()])
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
for country in countries.keys():
    local_attraction = attractiveness.copy()
    local_attraction[local_attraction.index.isin(neighbors(country))] += 1
    migration_map[country] = local_attraction

print("Migrating...")

def migrate_array(a):
    for country, population in a.groupby("Location"):
        for index, row in population.iterrows():
            local_attraction = migration_map[country]
            a.loc[index, "Location"] = df.sample(weights=local_attraction).index[0]
    return a

# Garbage collect before creating new processes.
gc.collect()
with Pool(THREADS) as p:
    g = pd.concat(p.map(migrate_array,
                        np.array_split(world[world.Migration > MIGRATION_THRESHOLD],
                                       THREADS * SPLITS)))
    p.close()
    p.join()
world = pd.concat([world, g], copy=False)
print((world.Location.value_counts() - world.Country.value_counts()).sort_values())
