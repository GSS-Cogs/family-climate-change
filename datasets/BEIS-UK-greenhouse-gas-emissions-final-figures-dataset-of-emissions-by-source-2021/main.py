# -*- coding: utf-8 -*-
#
# ## BEIS-UK-greenhouse-gas-emissions-final-figures-dataset-of-emissions-by-source-2021

import json
import pandas as pd
from gssutils import *

metadata = Scraper(seed="info.json")

distribution = metadata.distribution(
    mediaType="text/csv",
    latest=True,
    title=lambda x: "2021 UK greenhouse gas emissions: final figures – dataset of emissions by source"
    in x,
)

df = distribution.as_pandas(encoding="ISO-8859-1").fillna(" ")

df.loc[
    (df["National Communication Sub-sector"] == "(blank)"),"National Communication Sub-sector",] = "Not Applicable"
df.rename(columns={"ActivityName": "Activity Name", "Emissions (MtCO2e)": "Value"}, inplace=True)    
df.drop(columns="TerritoryName", axis=1, inplace=True)
df.drop(df.columns[df.columns.str.contains("Unnamed", case=False)], axis=1, inplace=True)

# Fixing BEIS' use of slashes in some columns:
df["National Communication Category"] = df["National Communication Category"].str.replace("/", "-")
df["National Communication Fuel"] = df["National Communication Fuel"].str.replace("/", "-")
df["Activity Name"] = df["Activity Name"].str.replace("/", "-")
df["Source"] = df["Source"].str.replace("/", "-").str.replace("-+", "-", regex=True)

df['Value'] = pd.to_numeric(df['Value'], errors="raise", downcast="float")
df["Value"] = df["Value"].astype(float).round(3)

for col in df.columns.values.tolist()[4:-2]:
    if col == 'Source':
        continue
    else:
        try:
            df[col] = df[col].apply(pathify)
        except Exception as err:
            raise Exception('Failed to pathify column "{}".'.format(col)) from err

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
         'Value']]

df.to_csv("observations.csv", index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file("catalog-metadata.json")
