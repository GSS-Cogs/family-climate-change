# -*- coding: utf-8 -*-
#
# ## BEIS-2020-UK-greenhouse-gas-emissions-final-figures-dataset-of-emissions-by-source

import json
import pandas as pd
from gssutils import *

info = json.load(open("info.json"))
metadata = Scraper(seed="info.json")

metadata.dataset.family = 'climate-change'
metadata.dataset.title = info['title']

distribution = metadata.distribution(
    mediaType="text/csv",
    latest=True,
    title=lambda x: "UK greenhouse gas emissions: final figures – dataset of emissions by source"
    in x,
)
df = distribution.as_pandas(encoding="ISO-8859-1").fillna(" ")

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

df = df.replace({'IPCC Code': {'2.00E+01': '20',
                                '4.00E+01': '40',
                                '4.00E+02': '400'
}})

df['Value'] = pd.to_numeric(df['Value'], errors="raise", downcast="float")
df["Value"] = df["Value"].astype(float).round(3)
df["Measure"] = df["Measure"].str.replace("MtCO2e, ", "")

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

df.to_csv("observations.csv", index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file("catalog-metadata.json")