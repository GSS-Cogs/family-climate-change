# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.7
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# This issue related to only the last 4 columns in the raw.csv, which describes index values for Energy Intensity Extract. Note the Thes rest of the data is transformed in a seperate folder called BEIS-Energy-Intensity-Extract-Index
#

import pandas as pd 
from gssutils import *
from csvcubed.models.cube.qb.catalog import CatalogMetadata

df = pd.read_csv('raw.csv', encoding='ISO-8859-1')

df = df.drop(columns=df.columns[1:13])

#Measure types / units to be extracted 
val_vars =[ "Consumption per passenger km \nIndex (2000 = 100)",
           "Energy consumption per household \nIndex (2000 = 100)",
           "Industry - Consumption per unit of output\nIndex (2000 = 100)",
           "Services (excluding agriculture) - Consumption per unit of output\nIndex (2000 = 100)"
          ]
other_vars = df.columns.difference(val_vars)

df = pd.melt(df, id_vars=other_vars, value_vars=val_vars, var_name='Measure Type',value_name='Value')

df = df.replace(r'\n','', regex=True) 
df['Unit'] = "Index (2000 = 100)"
df['Measure Type'] = df['Measure Type'].str.rstrip('Index (2000 = 100)')
df['Measure Type'] = df['Measure Type'].apply(pathify)
df['Measure Type'] = df['Measure Type'].replace("energy-consumption-per-househol",'energy-consumption-per-household') 
df['Unit'] = df['Unit'].apply(pathify)
df = df.dropna(subset=['Value'])

# +

df = df[['Year', 'Measure Type', 'Unit', 'Value']]
# -

df.to_csv('observations.csv', index=False)
catalog_metadata = CatalogMetadata(
    title = "Energy Intensity - Extract Index",
    description = "The publication provides the final extract of BEIS Energy Intensity Extract Index for 2020"
)
catalog_metadata.to_json_file('catalog-metadata.json')
