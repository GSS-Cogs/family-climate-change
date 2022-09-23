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
        geographic_coverage = 'United Kingdom'
        inclusions = 'None'

        dimensions = [
            HDim(period, "Period", DIRECTLY, ABOVE),
            HDim(nc_category, "NC Category", DIRECTLY, LEFT),
            HDim(nc_sector, "NC Sector", CLOSEST, ABOVE),
            HDimConst("Gas", gas),
            HDimConst("Geographic Coverage", geographic_coverage),
            HDimConst("Inclusions-Exclusions", inclusions)
        ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        df = tidy_sheet.topandas()
        indexNames = df[df["NC Category"] == ""].index
        df.drop(indexNames, inplace=True)
        tidied_sheets.append(df)

    elif tab.name == "3_1":
        cell = tab.filter("Geographic coverage")
        stop_cell = tab.filter("Total greenhouse gas emissions reported to the UNFCCC").expand(RIGHT).expand(DOWN)
        period = cell.shift(2).fill(RIGHT).is_not_blank().is_not_whitespace()
        gas = cell.shift(2).fill(DOWN).is_not_blank().is_not_whitespace() - stop_cell
        inclusions = cell.shift(1).fill(DOWN).is_not_blank().is_not_whitespace() - stop_cell

        geographic_coverage = cell.fill(DOWN).is_not_blank().is_not_whitespace() - stop_cell

        observations = period.waffle(gas)

        dimensions = [
            HDim(period, "Period", DIRECTLY, ABOVE),
            HDim(gas, "Gas", DIRECTLY, LEFT),
            HDim(inclusions, "Inclusions-Exclusions", CLOSEST, ABOVE),
            HDim(geographic_coverage, "Geographic Coverage", CLOSEST, ABOVE),
        ]
        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        df = tidy_sheet.topandas()
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

# Fix missing sub-sector
# combustion_categories = ["Stationary and mobile combustion", "Incidental lubricant combustion in engines - agriculture"]
# df.loc[df["NC Category"].isin(combustion_categories), "NC Category"] = "Combustion"
 
df["NC Sector"] = df["NC Sector"].str.replace("/", "-")
df["NC Category"] = df["NC Category"].str.replace("/", "-")

badInheritance = [
    "Aviation between UK and Crown Dependencies",
    "Shipping between UK and Crown Dependencies",
    "Aviation between UK and Overseas Territories",
    "Shipping between UK and Overseas Territories",
    "Aviation between the Crown Dependencies and Overseas Territories"
]
# -
df["Breakdown"] = df.apply(
    lambda x: "" if x["Geographic Coverage"] in badInheritance else x["Breakdown"],
    axis=1,
)

# +
df["Breakdown"] = df.apply(
    lambda x: "None" if x["Geographic Coverage"] in badInheritance else x["Breakdown"],
    axis=1,
)

df = df.replace(
    {
        "Geographic Coverage": {"United Kingdom only": "United Kingdom"}
    }
)
# -

indexNames = df[df["Breakdown"] == "Net emissions/removals from LULUCF"].index
df.drop(indexNames, inplace=True)

indexNames = df[df["Gas"] == "Total"].index
df.drop(indexNames, inplace=True)

# +
df = df.replace(
    {
        "Breakdown": {
            "Excluding net emissions/removals from land use, land use change and forestry (LULUCF)": "Excluding net emissions and removals from LULUCF"
        }
    }
)

df["Breakdown"] = df["Breakdown"].str.replace("/", " and ")

df = df.replace({'Gas' : {'Nitrous Oxide N2O' : 'Nitrous oxide (N2O)',
                          'Methane CH4' : 'Methane (CH4)',
                          'Carbon Dioxide CO2' :'Carbon dioxide (CO2)'}})
# -

df.rename(
    columns={"NC Category": "NC Sub sector"},inplace=True)

df = df.fillna("")

df = df.replace(
    {   
        "NC Sector": {"": "All sectors"},
        "NC Sub sector": {"": "All sub-sectors"}
    })

for col in ['NC Sector', 'NC Sub sector']:
    try:
        df[col] = df[col].apply(pathify)
    except Exception as err:
        raise Exception('Failed to pathify column "{}".'.format(col)) from err

df = df.drop_duplicates()

df = df[
    [
        "Period",
        "NC Sector",
        "NC Sub sector",
        "Geographic Coverage",
        "Breakdown",
        "Gas",
        "Value",
    ]
]

df.to_csv("observations.csv", index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file("catalog-metadata.json")