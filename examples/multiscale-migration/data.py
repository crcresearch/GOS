import numpy as np
import pandas as pd

def file_path(name):
    """
    Shortcut function to get the relative path to the directory
    which contains the data.
    """
    return "./data/%s" % name

def country_codes():
    """
    Build country rows from their names, ISO codes, and Numeric
    Country Codes.
    """
    return (
        pd.read_csv(
            file_path(
                "Country_List_ISO_3166_Codes_Latitude_Longitude.csv"),
            usecols=[0, 2, 3],
            index_col=1,
            keep_default_na=False))

def freedom_index():
    """
    Read data from the Freedom Index.
    """
    # TODO: Add xlrd to requirements.
    xl = pd.ExcelFile(file_path("Freedom_index.xlsx"))
    return xl.parse(1)

def ab_values():
    """
    Read generated A/B values for each country.
    """
    return pd.read_excel(file_path("A&B values for RTS.xlsx")).T

def passport_index():
    """
    Read data from the Passport Index.
    """
    return pd.read_excel(file_path("PassportIndex.xlsx"))

def un_stock():
    """
    Read from "Trends in International Migrant Stock: Migrants by
    Destination and Origin"
    """
    un_pd = pd.read_excel(
        file_path(
            "UN_MigrantStockByOriginAndDestination_2015.xlsx"
        ),
        skiprows=15
    )
    un_np = np.array(un_pd)
    ccountry_names = un_np[:,1]
    num_codes = un_np[:,3]
    return un_pd
