# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.5
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# ## DEFRA-Carbon-Footprint-Summary-Source-Region-90-18

import json 
import pandas as pd 
from gssutils import *
from pathlib import Path
import shutil
from gssutils.csvw.mapping import CSVWMapping

df = pd.read_csv('raw.csv', skiprows=2)

df = df.drop(columns='Unnamed: 0')
df.rename(columns={'Unnamed: 1': 'Period'}, inplace=True)

# +
df = pd.melt(df, id_vars=['Period'], var_name='Country Code', value_name='Value')
df = df.replace({'Total' : 'All'})
df['Period'] = df['Period'].map(lambda x: 'year/' + str(x))
df['Value'] = df['Value'].astype(str).astype(float).round(3)
df['Unit'] = 'Ktonnes CO2e'

df['Country Code'] = df['Country Code'].apply(pathify)
df = df[['Period', 'Country Code', 'Value', 'Unit']]
# -

out = Path('out')
out.mkdir(exist_ok=True)
df.to_csv(out/'summary-source-region.csv', index = False)

# Metadata.json file is created manually as dataset was received as as raw csv file 
with open('info.json') as f:
    info_json = json.load(f)
csvw_mapping = CSVWMapping()
csvw_mapping.set_mapping(info_json)
csvw_mapping.set_csv(out/'summary-source-region.csv')
csvw_mapping.set_dataset_uri(f"http://gss-data.org.uk/data/gss_data/climate-change/{info_json['id']}")
csvw_mapping.write(out/'summary-source-region.csv-metadata.json')

# metadata.trig file is manually created as dataset was received as as raw csv file
shutil.copy("summary-source-region.csv-metadata.trig", out/"summary-source-region.csv-metadata.trig")


