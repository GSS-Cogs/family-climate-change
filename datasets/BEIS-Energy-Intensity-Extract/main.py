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

# +
df = pd.read_csv('raw.csv', encoding='ISO-8859-1')
df = df.drop(columns=df.columns[13:17])
    
#Measure types / units to be extracted 
val_vars =[ "Road Passenger Consumption (ktoe)",
"Output (billion passenger kilometres)", 
"Energy consumption per unit of output (ktoe)",
"Total Final Domestic Consumption (ktoe)",
"No Households ('000s)",
"Consumption per household (ktoe)",
"Industrial Consumption (ktoe)",
"Industrial Output",
"Consumption per unit of output (ktoe)",
"Services Consumption, excluding agriculture  (ktoe)",
"Services Output",
"Energy consumption per unit of output (ktoe).1",
          ]
other_vars = df.columns.difference(val_vars)
df = pd.melt(
    df, 
    id_vars=other_vars, 
    value_vars=val_vars, 
    var_name='Measure Type',
    value_name='Value'
)

# +
df["Unit"]= df['Measure Type'].str.extract('.*\((.*)\).*')
df['Measure Type'] = df['Measure Type'].str.rstrip(' .1')
df['Measure Type'] = df['Measure Type'].str.replace(r"\(.*\)","").str.strip()
df = df.replace({'Measure Type' : {'No Households' : "No Households ('000s)"}})
df = df.replace({'Unit' : {"'000s" : "count",}})
df['Measure Type'] = df['Measure Type'].apply(pathify)
df["Unit"].fillna("UNKNOWN", inplace = True)
df['Unit'] = df['Unit'].apply(pathify)

df['Sector'] =  df['Measure Type']
sector_values = {
    'road-passenger-consumption' : 'road',
    'output': 'housing',
    'energy-consumption-per-unit-of-output': 'industrial',
    'total-final-domestic-consumption' : 'services',
    'no-households-000s': 'housing',
    'consumption-per-household': 'housing',
    'industrial-consumption' : 'industrial', 
    'industrial-output': 'industrial',
    'consumption-per-unit-of-output': 'industrial',
    'services-consumption-excluding-agriculture': 'services',
    'services-output' : 'services'
}
df['Sector'] = df['Sector'].replace(sector_values)
df
# -

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
csvw_mapping.set_dataset_uri(f"http://gss-data.org.uk/data/gss_data/climate-change/{info_json['id']}")
csvw_mapping.write(out/'energy.csv-metadata.json')

shutil.copy("energy.csv-metadata.trig", out/"energy.csv-metadata.trig")
