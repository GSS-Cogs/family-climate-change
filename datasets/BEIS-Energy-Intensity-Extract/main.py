# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.5
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

import pandas as pd 
from gssutils import *
import numpy as np
from csvcubed.models.cube.qb.catalog import CatalogMetadata
from datetime import datetime

df = pd.read_csv('raw.csv', encoding='ISO-8859-1')

df = df.drop(columns=df.columns[13:17])

#Measure types / units to be extracted 
val_vars =[ "Road Passenger Consumption (ktoe)", #(ROAD)
"Output (billion passenger kilometres)", #(ROAD)
"Energy consumption per unit of output (ktoe)", #(ROAD)
"Total Final Domestic Consumption (ktoe)", #(HOUSEHOLD)
"No Households ('000s)", #(HOUSEHOLD)
"Consumption per household (ktoe)", #(HOUSEHOLD)
"Industrial Consumption (ktoe)", #(INDUSTRIAL)
"Industrial Output", #(INDUSTRIAL)
"Consumption per unit of output (ktoe)", #(INDUSTRIAL)
"Services Consumption, excluding agriculture  (ktoe)", #(SERVICES)
"Services Output", #(SERVICES)
"Energy consumption per unit of output (ktoe).1", #(SERVICES)
          ]
other_vars = df.columns.difference(val_vars)          

# +

df = pd.melt(df, id_vars=other_vars, value_vars=val_vars, var_name='Measure Type',value_name='Value')
# -

df['Sector'] =  df['Measure Type']
sector_values = {
    "Road Passenger Consumption (ktoe)" : "road", 
    "Output (billion passenger kilometres)" : "road",
    "Energy consumption per unit of output (ktoe)" : "road",
    "Total Final Domestic Consumption (ktoe)" : "household",
    "No Households ('000s)": "household",
    "Consumption per household (ktoe)": "household",
    "Industrial Consumption (ktoe)": "industrial",
    "Industrial Output": "industrial",
    "Consumption per unit of output (ktoe)": "industrial",
    "Services Consumption, excluding agriculture  (ktoe)": "services",
    "Services Output": "services",
    "Energy consumption per unit of output (ktoe).1": "services"
}

df['Sector'] = df['Sector'].replace(sector_values)
df["Unit"]= df['Measure Type'].str.extract('.*\((.*)\).*')
df['Measure Type'] = df['Measure Type'].str.strip()
df['Measure Type'] = df['Measure Type'].str.replace(r"\(.*\)","").str.strip()
df = df.replace({'Measure Type' : {'No Households' : "No Households ('000s)"}})
df = df.replace({'Unit' : {"'000s" : "count",}})
df['Measure Type'] = df['Measure Type'].apply(pathify)
df["Unit"].fillna("UNKNOWN", inplace = True)
df['Unit'] = df['Unit'].apply(pathify)
df = df.replace(r'^\s*$', np.nan, regex=True)
df = df.dropna(subset=['Value'])

df['Value'] = pd.to_numeric(df['Value'], errors="raise", downcast="float")
df["Value"] = df["Value"].astype(float).round(3)

df = df[['Year', 'Measure Type', 'Sector', 'Unit', 'Value']]

df.to_csv('observations.csv', index=False)
catalog_metadata = CatalogMetadata(
    title = "Energy Intensity Extract",
    description = "The publication provides the final extract of BEIS Energy Intensity for 2020"
)
catalog_metadata.to_json_file('catalog-metadata.json')
