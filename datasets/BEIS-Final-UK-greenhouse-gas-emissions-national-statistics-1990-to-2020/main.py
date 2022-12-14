#!/usr/bin/env python
# coding: utf-8
# +
# ## BEIS-Final-UK-greenhouse-gas-emissions-national-statistics-1990-to-2020

# %%

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
# %%
tabs = distribution.as_databaker()
tabs = [
    tab for tab in tabs if tab.name in ["1_1", "1_2", "1_3", "1_4", "1_5", "1_6", "3_1"]
]
tidied_sheets = []
for tab in tabs:
    if tab.name in [ "1_2", "1_3", "1_4", "1_5", "1_6"]:
        cell = tab.filter("NC Sector")
        period = cell.shift(RIGHT).fill(RIGHT).is_not_blank().is_not_whitespace()
        unit = "Million of tonnes of carbon dioxide equivalent (MtCO2e)"
        stop_cell = tab.filter("Grand Total").fill(DOWN).fill(RIGHT)
        nc_category = tab.filter("NC Category").fill(DOWN) - stop_cell
        nc_sector = nc_category.is_blank().shift(LEFT)
        nc_sub_sector = nc_category.shift(LEFT).is_not_blank()

        if tab.name == "1_2":
            gas = "total-greenhouse-gases"
        elif tab.name == "1_3":
            gas = "Carbon Dioxide CO2"
        elif tab.name == "1_4":
            gas = "Methane CH4"
        elif tab.name == "1_5":
            gas = "Nitrous Oxide N2O"
        elif tab.name == "1_6":
            gas = "total-fluorinated-gases"

        observations = period.waffle(nc_category).is_not_blank().is_not_whitespace()

        dimensions = [
            HDim(period, "Period", DIRECTLY, ABOVE),
            HDim(nc_sector, "NC Sector", CLOSEST, ABOVE),
            HDim(nc_sub_sector, "NC Sub Sector",CLOSEST, ABOVE),
            HDim(nc_category, "NC Category", DIRECTLY, LEFT),
            HDimConst("Gas", gas),
            HDimConst("Unit", unit)
        ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        df = tidy_sheet.topandas()
        tidied_sheets.append(df)
        # print(tab.name)

    elif tab.name == "3_1":
        cell = tab.filter("Geographic coverage")
        stop_cell = tab.filter("Total greenhouse gas emissions reported to the UNFCC").expand(DOWN).expand(RIGHT)

        period = cell.shift(2).fill(RIGHT).is_not_whitespace()
        gas = cell.shift(2).fill(DOWN).is_not_whitespace() - stop_cell
        inclusions = cell.shift(1).fill(DOWN).is_not_whitespace() - stop_cell

        geographic_coverage = cell.fill(DOWN).is_not_whitespace() - stop_cell

        observations = period.waffle(gas)
        unit = "Million of tonnes of carbon dioxide equivalent (MtCO2e)"

        dimensions = [
            HDim(period, "Period", DIRECTLY, ABOVE),
            HDim(gas, "Gas", DIRECTLY, LEFT),
            HDim(inclusions, "Inclusions-Exclusions", CLOSEST, ABOVE),
            HDim(geographic_coverage, "Geographic Coverage", CLOSEST, ABOVE),
            HDimConst("Unit", unit),
        ]
        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        df = tidy_sheet.topandas()
        tidied_sheets.append(df)
        # print(tab.name)
 # %%       
df = pd.concat(tidied_sheets, sort=False).fillna("")

# %%
df.rename(
    columns={
        "OBS": "Value","DATAMARKER": "Marker","Inclusions-Exclusions": "Breakdown",},inplace=True)

df["Value"] = pd.to_numeric(df["Value"], errors="raise", downcast="float")
df["Value"] = df["Value"].astype(float).round(4)

df["Period"] = df["Period"].astype(float).astype(int)
df['Period'] = 'year/' + df['Period'].astype(str)

df["NC Sub Sector"] = df.apply(
    lambda x: "" if x["NC Sub Sector"] == x["NC Sector"] else x["NC Sub Sector"],
    axis=1
)
# %%
# Fix missing sub-sector
combustion_categories = ["Stationary and mobile combustion", "Incidental lubricant combustion in engines - agriculture"]
df.loc[df["NC Category"].isin(combustion_categories), "NC Sub Sector"] = "Combustion"

def sector(row):
    if row["NC Category"] == "":
        if row["NC Sector"] == "":
            return("Grand Total")
        else:
            return(row["NC Sector"])
    else:
        return(row["NC Category"])

df["Sector"] =  df.apply(sector, axis=1)
 
df["Sector"] = df["Sector"].str.replace("/", "-")

assert not df['Sector'].isna().any()
assert not (df['Sector'] == "").any()

badInheritance = [
    "Aviation between UK and Crown Dependencies",
    "Shipping between UK and Crown Dependencies",
    "Aviation between the Crown Dependencies and Overseas Territories",
    "Aviation between UK and Overseas Territories",
    "Shipping between UK and Overseas Territories"
]
# -
df["Breakdown"] = df.apply(
    lambda x: "" if x["Geographic Coverage"] in badInheritance else x["Breakdown"],
    axis=1,
)

df["Breakdown"] = df.apply(
    lambda x: "None"
    if "" in x["Breakdown"] and x["Geographic Coverage"] in badInheritance
    else x["Breakdown"],
    axis=1,
)

# %%
df = df.replace(
    {
        "Geographic Coverage": {"United Kingdom only": "United Kingdom"},
    }
)

indexNames = df[df["Breakdown"] == "Net emissions/removals from LULUCF"].index
df.drop(indexNames, inplace=True)

indexNames = df[df["Gas"] == "Total"].index
df.drop(indexNames, inplace=True)
# %%

df = df.replace(
    {
        "Geographic Coverage": {"": "United Kingdom"},
        "Breakdown": {"": "All"},
    }
)

# %%
COLUMNS_TO_NOT_PATHIFY = ["Period", "Geographic Coverage", "Breakdown", "Value",]

for col in df.columns.values.tolist():
    if col in COLUMNS_TO_NOT_PATHIFY:
        continue
    try:
        df[col] = df[col].apply(pathify)
    except Exception as err:
        raise Exception('Failed to pathify column "{}".'.format(col)) from err

df = df.replace(
    {
        "Breakdown": {
            "Excluding net emissions/removals from land use, land use change and forestry (LULUCF)": "Excluding net emissions and removals from LULUCF"
        }
    }
)

df["Breakdown"] = df["Breakdown"].str.replace("/", " and ")


#Matching Gas dimension to the notations of the codelist it is mapped to. 
df = df.replace({'Gas' : {'carbon-dioxide-co2' : 'CO2',
                          'methane-ch4' : 'CH4',
                          'nitrous-oxide-n2o' :'N2O',
                          'hydrofluorocarbons-hfc' : 'HFCs',
                          'perfluorocarbons-pfc' : 'PFCs',
                          'sulphur-hexafluoride-sf6' : 'SF6',
                          'nitrogen-trifluoride-nf3' : 'NF3'
                          }})
# %%

df = df[
    [
        "Period",
        "Geographic Coverage",
        "Sector",
        "Gas",
        "Breakdown",
        "Value"
    ]
]
# %%
df = df.drop_duplicates()

df.to_csv("observations.csv", index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file("catalog-metadata.json")
