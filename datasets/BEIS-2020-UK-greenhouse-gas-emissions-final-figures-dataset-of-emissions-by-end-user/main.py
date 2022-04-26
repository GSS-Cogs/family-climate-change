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
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# ## BEIS-2020-UK-greenhouse-gas-emissions-final-figures-dataset-of-emissions-by-end-user

# + tags=[]
import pandas as pd
from gssutils import *
# -

metadata = Scraper(seed='info.json')

distribution = metadata.distribution(latest=True, mediaType="text/csv",
                                     title=lambda x: "UK greenhouse gas emissions: final figures – dataset of emissions by end user" in x)

df = distribution.as_pandas(encoding='ISO-8859-1').fillna(' ')

df.loc[
    (df["National Communication Sub-sector"] == "(blank)"),
    "National Communication Sub-sector",
] = "Not Applicable"
df.drop(columns="TerritoryName", axis=1, inplace=True)
df.rename(columns={"ActivityName": "Activity Name"}, inplace=True)
df.drop(
    df.columns[df.columns.str.contains("Unnamed", case=False)], axis=1, inplace=True
)

# Fixing BEIS' use of slashes in some columns:
df["National Communication Category"] = df[
    "National Communication Category"
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

df.drop(df.columns[df.columns.str.contains(
    'Unnamed', case=False)], axis=1, inplace=True)
df.query("(not `IPCC Code` == 'Aviation_Bunkers') & (not `IPCC Code` == 'Marine_Bunkers') & (not `IPCC Code` == 'non-IPCC')", inplace=True)

df = df.drop_duplicates()

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

for col in df.columns.values.tolist()[4:-1]:
    try:
        df[col] = df[col].apply(pathify)
    except Exception as err:
        raise Exception('Failed to pathify column "{}".'.format(col)) from err

df.to_csv('observations.csv', index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')
