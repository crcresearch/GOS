import numpy as np
import pandas as pd
from constants import MIN_POPULATION, POPULATION_SCALE


def csv_path(name):
    """
    Shortcut function to get the relative path to the directory
    which contains the CSV data.
    """
    return "./data/%s" % name


def population():
    """
    Read the population for each country.
    """
    pop_csv = pd.read_csv(csv_path("Population.csv"), thousands=',', index_col=0,
                          dtype={"Population": np.uint32})
    pop_csv = pop_csv[pop_csv["Population"] > MIN_POPULATION]
    pop_csv["Population"] = (pop_csv["Population"] * POPULATION_SCALE).astype("uint32")
    return pop_csv


def gdp():
    """
    Read the GDP for each country.
    """
    gdp_csv = pd.read_csv(csv_path("UN_GDP.csv"), index_col=0, usecols=[0, 3],
                          dtype={"Value": np.float32})
    gdp_csv.columns = ["GDP"]
    return gdp_csv


def employment():
    """
    Read the unemployment for each country.
    """
    return pd.read_csv(csv_path("CIA_Unemployment.csv"), index_col=0, usecols=[1, 2])


# This is a dictionary used to translate names that do not the ones used elsewhere.
# TODO: Use ISO3 codes for each country and map their names to their codes using a CSV.
alt_names = {
    "Russia (Soviet Union)": "Russia",
    "Hyderabad": "India",
    "North Yemen": "Yemen",
    "South Yemen": "Yemen",
    "North Vietnam": "Vietnam",
    "South Vietnam": "Vietnam",
    "Democratic Republic of Congo (Zaire)": "Democratic Republic of the Congo",
    "Sri Lanka (Ceylon)": "Sri Lanka",
    "Zimbabwe (Rhodesia)": "Zimbabwe",
    "Turkey/Ottoman Empire": "Turkey",
    "Yugoslavia (Serbia)": "Serbia",
    "Cote DÕIvoire": "Cote d'Ivoire",
    "Rumania": "Romania",
    "United States of America": "United States",
    "Myanmar (Burma)": "Myanmar",
    "DR Congo (Zaire)": "Democratic Republic of the Congo",
    "Yemen (North Yemen)": "Yemen",
    "Cambodia (Kampuchea)": "Cambodia",
    "Vietnam (North Vietnam)": "Vietnam",
    "Bosnia-Herzegovina": "Bosnia and Herzegovina",
    "Serbia (Yugoslavia)": "Serbia",
    "FYR": "Macedonia",
    "Madagascar (Malagasy)": "Madagascar",
    "Hyderabadh": "India",
    "Yemen, Rep.": "Yemen",
    "Venezuela, RB": "Venezuela",
    "Syrian Arab Republic": "Syria",
    "Slovak Republic": "Slovakia",
    "Russian Federation": "Russia",
    "Korea, Rep.": "South Korea",
    "Korea, Dem. People’s Rep.": "North Korea",
    "Macedonia, FYR": "Macedonia",
    "Lao PDR": "Laos",
    "Kyrgyz Republic": "Kyrgyzstan",
    "Iran, Islamic Rep.": "Iran"
}


def conflict():
    """
    Read and calculate conflict scores for each country.
    """
    conflict_csv = pd.read_csv(csv_path("ucdp-prio-acd-4-2016.csv"), usecols=[0, 1, 9, 10])
    conflict_csv["Location"] = conflict_csv["Location"].str.split(', ')
    conflict_csv["Location"] = conflict_csv["Location"].map(
        lambda y: [alt_names[x].strip() if x in alt_names else x for x in y])
    conflict_csv["Conflict"] = ((conflict_csv["Year"] - 1946) / 10 *
                                conflict_csv["IntensityLevel"] ** 2)
    conflict_data = (pd.DataFrame(conflict_csv.Location.tolist(), index=conflict_csv.Conflict)
                     .stack().reset_index(level=1, drop=True)
                     .reset_index(name='Location')[['Location', 'Conflict']]
                     .groupby("Location").sum())
    return conflict_data


def neighbors():
    """
    Read the neighbors for each country.
    """
    neighbors_csv = pd.read_csv(csv_path("Neighbors.csv"), usecols=[0, 2, 4], index_col=1)
    neighbors_csv["neighbors"] = neighbors_csv["neighbors"].str.split()
    neighbors_csv["neighbors"] = neighbors_csv["neighbors"].map(
        lambda x: [item for sublist in
                   [neighbors_csv[neighbors_csv.iso_alpha2 == y].index for y in x]
                   for item in sublist], na_action='ignore')
    # Island nations are a weird exception
    neighbors_csv["neighbors"]["Madagascar"] = ["Mozambique", "South Africa", "Tanzania"]
    neighbors_csv["neighbors"]["Taiwan"] = ["China", "Philippines"]
    neighbors_csv["neighbors"]["New Zealand"] = ["Australia"]
    neighbors_csv["neighbors"]["Australia"] = ["New Zealand"]
    neighbors_csv["neighbors"]["Japan"] = ["Taiwan", "South Korea", "Philippines"]
    neighbors_csv["neighbors"]["Philippines"] = ["Taiwan", "South Korea", "Japan"]
    # TODO: Why isn't Norway getting any neighbors?
    neighbors_csv["neighbors"]["Norway"] = ["Sweden"]
    neighbors_csv["neighbors"]["Singapore"] = ["Malaysia", "Indonesia"]
    neighbors_csv["neighbors"]["Puerto Rico"] = ["United States", "Dominican Republic"]
    neighbors_csv["neighbors"]["Jamaica"] = ["Cuba", "Dominican Republic"]
    neighbors_csv["neighbors"]["Cuba"] = ["Jamaica", "Dominican Republic"]
    neighbors_csv["neighbors"]["Sri Lanka"] = ["India"]
    neighbors_csv["neighbors"]["France"] = ["Germany", "Switzerland", "Italy", "Belgium",
                                            "Luxembourg", "Spain", "Andorra"]
    return neighbors_csv


def fertility():
    """
    Read the fertiltiy rate for each country.
    """
    fertility_csv = pd.read_csv(csv_path("attachment.csv"), usecols=[1, 7], index_col=0)
    fertility_csv.columns = ["Fertility"]
    return fertility_csv


def net_migration():
    """
    Read net migration for all countries from 2007-2012.
    """
    net = pd.read_csv(csv_path("API_SM.POP.NETM_DS2_en_csv_v2.csv"),
                      usecols=[0, 56], header=2, index_col=0).dropna()
    net.columns = ["Net Migration"]
    net.index = net.index.map(lambda x: alt_names[x] if x in alt_names else x)
    return net


def all(fill_nan=True):
    """
    Join all data into a single DataFrame.
    """
    df = (population()
          .join(gdp())
          .join(employment())
          .join(conflict())
          .join(neighbors())
          .join(fertility())
          .join(net_migration()))
    if not fill_nan:
        return df
    # Some countries are missing data. We will guess this data using that of
    # neighboring countries.
    missing_cols = ["Conflict", "Unemployment", "GDP", "Fertility"]
    for _ in range(2):
        for column in missing_cols:
            for item, frame in df[df[column].isnull()]["neighbors"].iteritems():
                df.set_value(item, column, df[df.index.isin(frame)][column].mean())
    return df
