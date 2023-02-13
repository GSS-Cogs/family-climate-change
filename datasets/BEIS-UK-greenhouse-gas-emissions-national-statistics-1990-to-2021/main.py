#!/usr/bin/env python
# coding: utf-8
# +
# # +
# ## BEIS-UK-greenhouse-gas-emissions-national-statistics-1990-to-2021

import json
import pandas as pd
from gssutils import *

metadata = Scraper(seed="info.json")
metadata.dataset.title = "UK greenhouse gas emissions national statistics: 1990 to 2021"

distribution = metadata.distribution(
    mediaType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    title=lambda x: "2021 UK greenhouse gas emissions: final figures - data tables (Excel)"
    in x,
)

tabs = distribution.as_databaker()
tabs = [
    tab for tab in tabs if tab.name in ["1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "3.1"]
]

tidied_sheets = []
for tab in tabs:
    if tab.name == "1.1":
        cell = tab.filter("Gas")
        year = cell.fill(RIGHT).is_not_blank().is_not_whitespace()
        gas = cell.fill(DOWN).is_not_blank().is_not_whitespace()
        
        sector = "Grand Total"
        geographic_coverage = "United Kingdom"
        inclusions = "Including net emissions/removals from LULUCF"
        unit = "Million of tonnes of carbon dioxide equivalent (MtCO2e)"
        
        observations = year.waffle(gas)
        dimensions = [
            HDim(year, "Year", DIRECTLY, ABOVE),
            HDim(gas, "Gas", DIRECTLY, LEFT),
            HDimConst("Sector", sector),
            HDimConst("Geographic Coverage", geographic_coverage),
            HDimConst("Inclusions-Exclusions", inclusions),
            HDimConst("Unit", unit)
        ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        df = tidy_sheet.topandas()
        df.replace({"Gas": {"Net CO2 emissions (emissions minus removals)": "Carbon dioxide CO2",
                            "Total greenhouse gas emissions": "Total greenhouse gases"}}, inplace=True)
        tidied_sheets.append(df)

    elif tab.name in ["1.2", "1.3", "1.4", "1.5", "1.6"]:
        cell = tab.filter("NC Sector")
        year = cell.shift(RIGHT).fill(RIGHT).is_not_blank().is_not_whitespace()
        cell_to_remove = tab.filter("Grand Total")
        nc_category = tab.filter("NC Category").fill(DOWN) - cell_to_remove.shift(RIGHT).fill(DOWN)
        nc_sector = nc_category.is_blank().shift(LEFT) 
        nc_sub_sector = nc_category.shift(LEFT).is_not_blank()

        if tab.name == "1.2":
            gas = "Total greenhouse gases"
        elif tab.name == "1.3":
            gas = "Carbon dioxide CO2"
        elif tab.name == "1.4":
            gas = "Methane CH4"
        elif tab.name == "1.5":
            gas = "Nitrous oxide N2O"
        elif tab.name == "1.6":
            gas = "Fluorinated gases F gases"

        geographic_coverage = "United Kingdom"
        inclusions = "Including net emissions/removals from LULUCF"
        unit = "Million of tonnes of carbon dioxide equivalent (MtCO2e)"
        observations = year.waffle(nc_category).is_not_blank().is_not_whitespace()

        dimensions = [
            HDim(year, "Year", DIRECTLY, ABOVE),
            HDim(nc_sector, "NC Sector", CLOSEST, ABOVE),
            HDim(nc_sub_sector, "NC Sub Sector",CLOSEST, ABOVE),
            HDim(nc_category, "NC Category", DIRECTLY, LEFT),
            HDimConst("Gas", gas),
            HDimConst("Geographic Coverage", geographic_coverage),
            HDimConst("Inclusions-Exclusions", inclusions),
            HDimConst("Unit", unit)
        ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        df = tidy_sheet.topandas()
        tidied_sheets.append(df)

    elif tab.name == "3.1":
        cell = tab.filter("Geographic coverage")
        stop_cell = tab.filter("Total greenhouse gas emissions reported to the UNFCCC").expand(DOWN).expand(RIGHT)
        geographic_coverage = cell.fill(DOWN).is_not_whitespace() - stop_cell
        inclusions = cell.shift(1,0).fill(DOWN).is_not_whitespace() - stop_cell
        year = cell.shift(2,0).fill(RIGHT).is_not_whitespace()
        gas = cell.shift(2,0).fill(DOWN).is_not_whitespace() - stop_cell
        
        sector = "Grand Total"
        unit = "Million of tonnes of carbon dioxide equivalent (MtCO2e)"

        observations = year.waffle(gas)

        dimensions = [
            HDim(year, "Year", DIRECTLY, ABOVE),
            HDim(gas, "Gas", DIRECTLY, LEFT),
            HDimConst("Sector", nc_sector),
            HDim(inclusions, "Inclusions-Exclusions", CLOSEST, ABOVE),
            HDim(geographic_coverage, "Geographic Coverage", CLOSEST, ABOVE),
            HDimConst("Unit", unit),
        ]
        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        df = tidy_sheet.topandas()
        df.replace({'Gas': {'Total': 'Total greenhouse gases'}}, inplace=True)
        tidied_sheets.append(df)
df = pd.concat(tidied_sheets).fillna("")

df.rename(
    columns={
        "OBS": "Value","DATAMARKER": "Marker","Inclusions-Exclusions": "Breakdown",},inplace=True)

df["Value"] = pd.to_numeric(df["Value"], errors="raise", downcast="float")
df["Value"] = df["Value"].astype(float).round(4)

df["Year"] = df["Year"].astype(float).astype(int)

# Function to cleam up the redundant dimensions - NC Sub-sector and NC Category
def sector(row):
    if row["NC Category"] == "":
        if row["NC Sector"] == "":
            return("Grand Total")
        else:
            return(row["NC Sector"])
    else:
        return(row["NC Category"])

# Fix missing sub-sector - 'Combustion'
combustion_categories = ["Stationary and mobile combustion", "Incidental lubricant combustion in engines - agriculture"]
df.loc[df["NC Category"].isin(combustion_categories), "NC Sub Sector"] = "Combustion"

df["Sector"] =  df.apply(sector, axis=1)

assert not df['Sector'].isna().any()
assert not (df['Sector'] == "").any()

badInheritance = [
    "Aviation between UK and Crown Dependencies",
    "Shipping between UK and Crown Dependencies",
    "Aviation between the Crown Dependencies and Overseas Territories",
    "Aviation between UK and Overseas Territories",
    "Shipping between UK and Overseas Territories"
]

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

df.replace(
    {
        "Geographic Coverage": {"United Kingdom only": "United Kingdom"},
    }, inplace=True
)
df.replace(
    {
        "Breakdown": {
            "Excluding net emissions/removals from LULUCF": "Excluding net emissions and removals from LULUCF",
            "Including net emissions/removals from LULUCF": "Including net emissions and removals from LULUCF",
            "Net emissions/removals from LULUCF": "Net emissions and removals from LULUCF"
        }
    }, inplace=True
)

df.replace(
    {
        "Sector": {"Direct N2O emissions from N mineralization/immobilisation - Forest land": "Direct N2O emissions from N mineralization immobilisation - Forest land",
                    "Direct N2O emissions from N mineralization/immobilisation - Cropland": "Direct N2O emissions from N mineralization immobilisation - Cropland",
                    "Direct N2O emissions from N mineralization/immobilisation - Grassland": "Direct N2O emissions from N mineralization immobilisation - Grassland",
                    "Direct N2O emissions from N mineralization/immobilisation - Settlements": "Direct N2O emissions from N mineralization immobilisation - Settlements"
        }
    }, inplace=True
)

COLUMNS_TO_NOT_PATHIFY = ["Year", "Geographic Coverage", "Breakdown", "Value",]

for col in df.columns.values.tolist():
    if col in COLUMNS_TO_NOT_PATHIFY:
        continue
    try:
        df[col] = df[col].apply(pathify)
    except Exception as err:
        raise Exception('Failed to pathify column "{}".'.format(col)) from err

df["Breakdown"] = df["Breakdown"].str.replace("/", " and ")

#Matching Gas dimension to the notations of the codelist it is mapped to. 
df.replace({'Gas' : {'carbon-dioxide-co2' : 'CO2',
                          'methane-ch4' : 'CH4',
                          'nitrous-oxide-n2o' :'N2O',
                          'hydrofluorocarbons-hfc' : 'HFC',
                          'perfluorocarbons-pfc' : 'PFC',
                          'sulphur-hexafluoride-sf6' : 'SF6',
                          'nitrogen-trifluoride-nf3' : 'NF3',
                          "fluorinated-gases-f-gases": "F"
                    }
            }, inplace=True
)

df = df[
    [
        "Year",
        "Geographic Coverage",
        "Sector",
        "Gas",
        "Breakdown",
        "Value"
    ]
]
df = df.drop_duplicates()

df.to_csv("observations.csv", index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file("catalog-metadata.json")