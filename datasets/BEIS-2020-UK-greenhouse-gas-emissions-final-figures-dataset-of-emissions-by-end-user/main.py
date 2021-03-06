# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.7
#   kernelspec:
#     display_name: Python 3.9.10 64-bit
#     language: python
#     name: python3
# ---

# ## BEIS-2020-UK-greenhouse-gas-emissions-final-figures-dataset-of-emissions-by-end-user

# + tags=[]
import json
import pandas as pd
from gssutils import *
# -

info = json.load(open("info.json"))
metadata = Scraper(seed='info.json')

metadata.dataset.family = 'climate-change'
metadata.dataset.title = info['title']

distribution = metadata.distribution(latest=True, mediaType="text/csv",
                                     title=lambda x: "UK greenhouse gas emissions: final figures – dataset of emissions by end user" in x)

df = distribution.as_pandas(encoding='ISO-8859-1').fillna('')

df.drop(columns="TerritoryName", axis=1, inplace=True)
df.rename(columns={"ActivityName": "Activity Name"}, inplace=True)
df.drop(
    df.columns[df.columns.str.contains("Unnamed", case=False)], axis=1, inplace=True
)

# +
df.loc[
    (df["National Communication Sub-sector"] == "(blank)"),
    "National Communication Sub-sector",
] = "Not Applicable"

df.loc[
    (df["National Communication Sector"] == ''),
    "National Communication Sector",
] = "Not Applicable"

df.loc[(df['National Communication Category'] == ''), 'National Communication Category'] = 'Not Applicable'
df.loc[(df['National Communication Fuel'] == ''), 'National Communication Fuel'] = 'Not Applicable'
df.loc[(df['National Communication Fuel Group'] == ''), 'National Communication Fuel Group'] = 'Not Applicable'
# -

# Fixing BEIS' use of slashes in some columns:
df["National Communication Category"] = df[
    "National Communication Category"
].str.replace("/", "-")
df["Activity Name"] = df[
   "Activity Name"
].str.replace("/", "-")
df["National Communication Fuel"] = df[
    "National Communication Fuel"
].str.replace("/", "-")
df["Source"] = df["Source"].str.replace(
    "/", "-").str.replace("-+", "-", regex=True)

df = pd.melt(
    df,
    id_vars=[
        "GHG",
        "GHG Grouped",
        "IPCC Code",
        "Year",
        "National Communication Sector",
        "National Communication Sub-sector",
        "National Communication Category",
        "Source",
        "National Communication Fuel Group",
        "National Communication Fuel",
        "Activity Name",
    ],
    value_vars=["Emissions (MtCO2e, AR4 GWPs)",
                "Emissions (MtCO2e, AR5 GWPs)"],
    var_name="Measure",
    value_name="Value",
)

df['Value'] = pd.to_numeric(df['Value'], errors="raise", downcast="float")
df["Value"] = df["Value"].astype(float).round(3)
df["Measure"] = df["Measure"].str.replace("MtCO2e, ", "")

df.query("(not `IPCC Code` == 'Aviation_Bunkers') & (not `IPCC Code` == 'Marine_Bunkers') & (not `IPCC Code` == 'non-IPCC')", inplace=True)

df = df[['GHG',
         'GHG Grouped',
         'IPCC Code',
         'Year',
         'National Communication Sector',
         'National Communication Sub-sector',
         'National Communication Category',
         'Source',
         'National Communication Fuel Group',
         'National Communication Fuel',
         'Activity Name',
         'Measure',
         'Value']]

for col in df.columns.values.tolist()[4:-3]:
    if col == 'Source':
        continue
    else:
        try:
            df[col] = df[col].apply(pathify)
        except Exception as err:
            raise Exception('Failed to pathify column "{}".'.format(col)) from err

df = df.drop_duplicates()

df.to_csv('observations.csv', index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')
