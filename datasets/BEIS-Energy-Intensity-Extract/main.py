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

import json 
import pandas as pd 
from gssutils import *
from pathlib import Path
import shutil
from gssutils.csvw.mapping import CSVWMapping
import numpy as np

# +
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
df = pd.melt(
    df, 
    id_vars=other_vars, 
    value_vars=val_vars, 
    var_name='Measure Type',
    value_name='Value'
)
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
# -

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
df

out = Path('out')
out.mkdir(exist_ok=True)
df.to_csv(out/'energy.csv', index = False)

# ## No scraper present so we have created this manually

# +
with open('info.json') as f:
    info_json = json.load(f)
csvw_mapping = CSVWMapping()
csvw_mapping.set_mapping(info_json)
csvw_mapping.set_csv(out/"energy.csv")
csvw_mapping.set_dataset_uri(f"http://gss-data.org.uk/data/gss_data/climate-change/{info_json['id']}/energy-intensity-extract")
csvw_mapping.write(out/'energy.csv-metadata.json')

shutil.copy("energy.csv-metadata.trig", out/"energy.csv-metadata.trig")
# -

# ## Transforming index data (Last 4 columns seperately) 

# +
df = pd.read_csv('raw.csv', encoding='ISO-8859-1')
df = df.drop(columns=df.columns[1:13])
    
#Measure types / units to be extracted 
val_vars =[ "Consumption per passenger km \nIndex (2000 = 100)",
           "Energy consumption per household \nIndex (2000 = 100)",
           "Industry - Consumption per unit of output\nIndex (2000 = 100)",
           "Services (excluding agriculture) - Consumption per unit of output\nIndex (2000 = 100)"
          ]
other_vars = df.columns.difference(val_vars)
df = pd.melt(
    df, 
    id_vars=other_vars, 
    value_vars=val_vars, 
    var_name='Measure Type',
    value_name='Value'
)
df = df.replace(r'\n','', regex=True) 
df['Unit'] = "Index (2000 = 100)"
df['Measure Type'] = df['Measure Type'].str.rstrip('Index (2000 = 100)')
df['Measure Type'] = df['Measure Type'].apply(pathify)
df['Measure Type'] = df['Measure Type'].replace("energy-consumption-per-househol",'energy-consumption-per-household') 
df['Unit'] = df['Unit'].apply(pathify)
df = df.dropna(subset=['Value'])
df
# -

out = Path('out')
out.mkdir(exist_ok=True)
df.to_csv(out/'energy-intensity-extract-index.csv', index = False)

# +
with open('info.json') as f:
    info_json = json.load(f)
csvw_mapping = CSVWMapping()
csvw_mapping.set_mapping(info_json)
csvw_mapping.set_csv(out/"energy-intensity-extract-index.csv")
csvw_mapping.set_dataset_uri(f"http://gss-data.org.uk/data/gss_data/climate-change/{info_json['id']}/energy-intensity-extract-index")
csvw_mapping.write(out/'energy-intensity-extract-index.csv-metadata.json')

shutil.copy("energy-intensity-extract-index.csv-metadata.trig", out/"energy-intensity-extract-index.csv-metadata.trig")
