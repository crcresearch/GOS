# These libraries are used later to supply mathematical calculations.
import math
from math import e
from pathlib import Path

import gos

# Visualizaton
import numpy as np
import pandas as pd
import pytest
from haversine import haversine

dir_data = Path("./examples/multiscale-migration/data")


@pytest.fixture
def country_to_code() -> dict[str, str]:
    return (
        pd.read_csv(
            dir_data / "Country_List_ISO_3166_Codes_Latitude_Longitude.csv",
            usecols=[0, 2],
            index_col=0,
            keep_default_na=False,
        ).to_dict()["Alpha-3 code"]
        | pd.read_csv(dir_data / "other.csv", index_col=0).to_dict()["ISO"]
    )


def test_country_codes(country_to_code: dict[str, str]):
    assert country_to_code["Albania"] == "ALB"

    assert country_to_code["Bolivia"] == "BOL"
    assert country_to_code["Bolivia (Plurinational State of)"] == "BOL"
    assert country_to_code["Bolivia, Plurinational State of"] == "BOL"


@pytest.fixture
def code_to_country() -> dict[str, list[str]]:
    codes = (
        pd.read_csv(
            dir_data / "Country_List_ISO_3166_Codes_Latitude_Longitude.csv",
            usecols=[0, 2],
            index_col=1,
            keep_default_na=False,
        )
        .groupby("Alpha-3 code")["Country"]
        .apply(list)
        .to_dict()
    )

    other = pd.read_csv(dir_data / "other.csv", index_col=1).groupby("ISO")["Name"].apply(list).to_dict()
    for k, v in other.items():
        codes[k] = sorted(codes.get(k, []) + v)
    return codes


def test_code_to_country(code_to_country: dict[str, str]):
    assert code_to_country["ALB"] == ["Albania"]
    assert code_to_country["BOL"] == ["Bolivia", "Bolivia (Plurinational State of)", "Bolivia, Plurinational State of"]


@pytest.fixture
def expected_migrations(country_to_code: dict[str, str]):
    migrations = pd.read_excel(
        "./data/Net Population Change Caused by Migration.xls", usecols=[0, 9], skiprows=3, index_col=0
    )
    migrations.index = migrations.index.map(lambda x: country_to_code.get(x, x))
    return migrations.to_dict()["Net Population Change Caused by Migration"]


def test_parse_expected_migrations(expected_migrations):
    assert expected_migrations["ABW"] == 208.42737499999998


def compare_migrations(actual: dict[str, float], expected: dict[str, float]):
    # Find missing countries
    _ = set(actual.keys()) - set(expected.keys())
    # assert missing_from_expected == set()

    # Filter dictionaries
    actual: pd.DataFrame = pd.DataFrame.from_dict(actual, orient="index")
    expected: pd.DataFrame = pd.DataFrame.from_dict(expected, orient="index")

    # Find differences
    diff_raw = (expected - actual).dropna()
    print(diff_raw)

    # Calculate Statistics
    statistics = diff_raw.agg(["min", "max", "mean"])
    statistics.loc["rmse"] = math.sqrt((np.array(diff_raw) ** 2).mean() ** 0.5)
    print(statistics)

    return statistics


def test_validation(country_to_code, expected_migrations):
    column_names = ["Name", "Code"]

    def country_codes():
        """
        Build country rows from their names, ISO codes, and Numeric
        Country Codes.
        """
        cc = pd.read_csv(
            dir_data / "Country_List_ISO_3166_Codes_Latitude_Longitude.csv",
            usecols=[0, 2, 3],
            index_col=1,
            keep_default_na=False,
        )
        cc.columns = column_names
        return cc

    def other_codes():
        other_codes = pd.read_csv(dir_data / "other.csv", index_col=1)
        other_codes.columns = column_names[0:1]
        return other_codes

    world = gos.World(index=list(set(country_codes().index) | set(other_codes().index)))
    gos.Neighborhood.update(country_codes().groupby("Alpha-3 code")["Name"].apply(list).to_dict())
    gos.Neighborhood.update(other_codes().groupby("ISO")["Name"].apply(list).to_dict())
    gos.Neighborhood.update(country_codes().groupby("Alpha-3 code")["Code"].apply(list).to_dict())

    def freedom_index() -> pd.DataFrame:
        """
        Read data from the Freedom Index.
        """
        fi = pd.ExcelFile(dir_data / "Freedom_index.xlsx").parse(1).set_index("Country")
        fi.columns = ["Freedom Index"]
        fi.index = fi.index.map(lambda x: country_to_code.get(x, None))
        # fi.dropna()
        return fi

    fi = freedom_index()
    print(fi)

    def ab_values():
        """
        Read generated A/B values for each country.
        """
        ab = pd.read_excel(dir_data / "A&B values for RTS.xlsx").set_index("Country")
        ab.index = ab.index.map(lambda x: country_to_code.get(x, None))
        return ab

    ab = ab_values()
    print(fi)

    def passport_index():
        """
        Read data from the Passport Index.
        """
        pi = pd.read_excel(dir_data / "PassportIndex.xlsx").set_index("Country")
        pi.columns = ["Passport Index"]
        pi.index = pi.index.map(lambda x: country_to_code.get(x, None))
        return pi

    pi = passport_index()

    unemployment_data = pd.read_csv(dir_data / "CIA_Unemployment.csv", index_col=0, usecols=[1, 2])
    unemployment_data.index = unemployment_data.index.map(lambda x: country_to_code.get(x, None))
    unemployment_data["Unemployment"] /= 100

    # Population
    population = pd.read_csv(dir_data / "newPOP.csv").set_index("Country")
    population.index = population.index.map(lambda x: country_to_code.get(x, None))

    world.update_neighborhoods(ab)
    world.update_neighborhoods(pi)
    world.update_neighborhoods(unemployment_data)
    world.update_neighborhoods(population)
    world.update_neighborhoods(fi)

    lang_csv = pd.read_csv(dir_data / "languages.csv", index_col=0)
    lang_sets = [set([str(y).strip() for y in x[1] if y != " "]) for x in lang_csv.iterrows()]
    overlap = []
    for s in lang_sets:
        o = []
        for i in range(len(lang_sets)):
            o.append(len(lang_sets[i].intersection(s)) >= 1)
        overlap.append(o)
    lang_data = pd.DataFrame(overlap, index=lang_csv.index, columns=lang_csv.index)

    world.add_matrix("language", 1 - lang_data)
    print(1 - lang_data)

    un_pd = pd.read_excel(dir_data / "UN_MigrantStockByOriginAndDestination_2015.xlsx", skiprows=15)
    un_pd = un_pd.set_index("Unnamed: 1")
    un_pd = un_pd.iloc[0:275, 7:250]
    un_pd = un_pd.sort_index().fillna(1)

    world.add_matrix("un", un_pd)

    distance_frame = pd.read_csv(
        dir_data / "Country_List_ISO_3166_Codes_Latitude_Longitude.csv",
        usecols=[2, 4, 5],
        index_col=0,
        keep_default_na=False,
    )
    locations = [(x[1].iloc[0], x[1].iloc[1]) for x in distance_frame.iterrows()]

    rows = []
    for i in range(len(locations)):
        row = []
        for loc in locations:
            row.append(haversine(loc, locations[i]))
        rows.append(row)
    distance = pd.DataFrame(rows, distance_frame.index, distance_frame.index)
    distance = distance / distance.max().max()

    world.add_matrix("distance", distance)

    pd.options.mode.chained_assignment = None

    world.update_neighborhoods(pd.Series(world.data["A"] * e ** (world.data["B"] * 1)), "rts")
    world.update_neighborhoods(pd.Series(world.data["A"] * e ** (world.data["B"] * 82)), "beta")

    rows = []
    for i in range(len(world.data["Freedom Index"])):
        row = []
        for freedom_index in world.data["Freedom Index"]:
            diff = (world.data["Freedom Index"].iloc[i] - freedom_index) / 100.0
            row.append(diff)
        rows.append(row)

    fi_diff = pd.DataFrame(rows, world.data["Freedom Index"].index, world.data["Freedom Index"].index)

    # default delta values, do not edit this cell
    delta1 = 0.1
    delta2 = 0.9
    political_barriers = delta1 * world.data["Passport Index"] / 100.0 + delta2 * (1 - fi_diff)

    # default gamma values, do not edit this cell
    gamma1 = 0.5
    gamma2 = 0.5

    OM = world.matrices["un"].sort_index(axis=1).sort_index(axis=0) / world.data["Population"]
    # transpose UN matrix for this calculation so that we are dividing by population of destination
    EE = world.matrices["un"].T.sort_index(axis=1).sort_index(axis=0) / world.data["Population"]
    EE = EE.T
    MH = gamma1 * (OM) + gamma2 * (EE)
    max_MH = MH.max().nlargest(10).mean()
    MH = 1 - (MH / max_MH)
    MH[MH < 0] = 0

    # default alpha values, do not edit this cell
    alpha1 = 0.3
    alpha2 = 0.5
    alpha3 = 0.1
    alpha4 = 0.1

    # Cost
    cost = (
        alpha1 * world.matrices["distance"]
        + alpha2 * MH
        + alpha3 * world.matrices["language"]
        + alpha4 * political_barriers
    ) * world.data["beta"]

    wages = (1 - world.data["Unemployment"]) * world.data["rts"]

    migration = (
        pd.DataFrame(
            np.array([[x] * len(world.data) for x in wages.values]) - np.array([list(wages.values)] * len(world.data)),
            world.data.index,
            world.data.index,
        )
        - cost
    ).clip(lower=0)

    migration = migration / (migration.sum() + 1)
    migration = migration / migration.sum(axis=1).max()

    # TODO: Why does this require being transposed?
    migration = (0.15 * migration.transpose() * world.data["Population"]).transpose()

    net_migration = migration.sum(axis=1) - migration.sum()

    statistics = compare_migrations(net_migration.to_dict(), expected_migrations)
    assert statistics.loc["rmse"][0] == 724.5124898816618
