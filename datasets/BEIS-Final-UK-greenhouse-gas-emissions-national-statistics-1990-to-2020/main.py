#!/usr/bin/env python
# coding: utf-8
# ### BEIS-Final-UK-greenhouse-gas-emissions-national-statistics-1990-to-2020

# +
import json
import pandas as pd
from gssutils import *

metadata = Scraper(seed="info.json")

distribution = metadata.distribution(
    latest=True,
    mediaType="application/vnd.oasis.opendocument.spreadsheet",
    title=lambda x: "UK greenhouse gas emissions: final figures - data tables (alternative ODS format)"
    in x,
)
# -
tabs = distribution.as_databaker()
tabs = [
    tab for tab in tabs if tab.name in ["1_1", "1_2", "1_3", "1_4", "1_5", "1_6", "3_1"]
]
tidied_sheets = []
for tab in tabs:
    
    if tab.name in ["1_3", "1_4", "1_5", "1_6"]:
        cell = tab.filter("NC Sector")
        period = cell.shift(RIGHT).fill(RIGHT).is_not_blank().is_not_whitespace()
        stop_cell = tab.filter("Grand Total").expand(RIGHT).expand(DOWN)
        nc_category = tab.filter("NC Category").fill(DOWN) - stop_cell
        nc_sector = nc_category.is_blank().shift(LEFT)
        
        if tab.name == "1_3":
            gas = "Carbon Dioxide CO2"
        elif tab.name == "1_4":
            gas = "Methane CH4"
        elif tab.name == "1_5":
            gas = "Nitrous Oxide N2O"
        elif tab.name == "1_6":
            gas = "Fluorinated Gases (F Gases)"

        observations = period.waffle(nc_category).is_not_blank().is_not_whitespace()
        
        dimensions = [
            HDim(period, "Period", DIRECTLY, ABOVE),
            HDim(nc_category, "NC Category", DIRECTLY, LEFT),
            HDim(nc_sector, "NC Sector", CLOSEST, ABOVE),
            HDimConst("Gas", gas)
        ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        df = tidy_sheet.topandas()
        indexNames = df[df["NC Category"] == ""].index
        df.drop(indexNames, inplace=True)
        tidied_sheets.append(df)
df = pd.concat(tidied_sheets, ignore_index=True)

# +
df.rename(
    columns={
        "OBS": "Value","DATAMARKER": "Marker",
        "Inclusions-Exclusions": "Breakdown",
        },inplace=True)

df["Value"] = pd.to_numeric(df["Value"], errors="raise", downcast="float")
df["Value"] = df["Value"].astype(float).round(3)
df["Period"] = df["Period"].astype(float).astype(int)
df['Period'] = 'year/' + df['Period'].astype(str)

# # Fix missing sub-sector
# combustion_categories = ["Stationary and mobile combustion", "Incidental lubricant combustion in engines - agriculture"]
# df.loc[df["NC Category"].isin(combustion_categories), "NC Sub-sector"] = "Combustion"
 
df["NC Sector"] = df["NC Sector"].str.replace("/", "-")
df["NC Category"] = df["NC Category"].str.replace("/", "-")
# -
df = df.replace(
    {
        "Geographic Coverage": {"United Kingdom only": "United Kingdom"}
    }
)

df = df.replace({'Gas' : {'Nitrous Oxide N2O' : 'Nitrous oxide (N2O)',
                          'Methane CH4' : 'Methane (CH4)',
                          'Carbon Dioxide CO2' :'Carbon dioxide (CO2)'}})

# +
# df.rename(
#     columns={"NC Category": "NC Sub Sector"},inplace=True)
# -

for col in ['NC Sector', 'NC Category']:
    try:
        df[col] = df[col].apply(pathify)
    except Exception as err:
        raise Exception('Failed to pathify column "{}".'.format(col)) from err

df = df.drop_duplicates()

df = df[
    [
        "Period",
        "NC Sector",
        "NC Category",
        "Gas",
        "Value",
    ]
]

df.to_csv("observations.csv", index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file("catalog-metadata.json")