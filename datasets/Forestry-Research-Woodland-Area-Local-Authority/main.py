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

# ## Forestry-Research-Woodland-Area-Local-Authority

import json
import pandas as pd
from gssutils import *
from pathlib import Path
import shutil
from gssutils.csvw.mapping import CSVWMapping

# +
df = pd.read_csv('raw.csv', skiprows=2, encoding='ISO-8859-1')
# 17 blank rows at bottom need to be dropped. 
n = 17
df.drop(df.tail(n).index, inplace = True)

#Measure types / units to be extracted 
val_vars =[ "Standard_area_measurement _hectares",
"Woodland_hectares", 
"Woodland_%"]
other_vars = df.columns.difference(val_vars)
df = pd.melt(
    df, 
    id_vars=other_vars, 
    value_vars=val_vars, 
    var_name='Measure Type',
    value_name='Value'
)
df.rename(columns={'Local_authority_Area': 'Local Authority Area'}, inplace=True)
#add unit dimension based of Measure Type 
df['Unit'] = df['Measure Type'].apply(lambda x: 'hectares' if 'hectares' in x else 'percentage')
df = df.replace({'Measure Type' : {'Standard_area_measurement _hectares' : "standard-area-measurement",
                                  'Woodland_hectares' : 'woodland',
                                  'Woodland_%' : 'woodland'}})
df['Year'] = '2019'
df = df[['Year', 'Code', 'Value', 'Measure Type', 'Unit']]
df.rename(columns={'Code' : 'Local Authority Area'}, inplace=True)
# -

out = Path('out')
out.mkdir(exist_ok=True)
df.to_csv(out/'forestry-research-woodland-area-local-authority.csv', index = False)

# ## No scraper present so we have created this manually

# +
with open('info.json') as f:
    info_json = json.load(f)
csvw_mapping = CSVWMapping()
csvw_mapping.set_mapping(info_json)
csvw_mapping.set_csv(out/"forestry-research-woodland-area-local-authority.csv")
csvw_mapping.set_dataset_uri(f"http://gss-data.org.uk/data/gss_data/climate-change/{info_json['id']}")
csvw_mapping.write(out/'forestry-research-woodland-area-local-authority.csv-metadata.json')

shutil.copy("forestry-research-woodland-area-local-authority.trig", out/"forestry-research-woodland-area-local-authority.trig")
# -




