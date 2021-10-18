#!/usr/bin/env python
# coding: utf-8

# In[5]:


# ## DEFRA-Carbon-Footprint-GHG-coicop

import json
import shutil
import pandas as pd
from gssutils import *
from pathlib import Path
from gssutils.csvw.mapping import CSVWMapping

df = pd.read_csv('raw.csv', encoding='ISO-8859-1')
df.rename(columns={'Unnamed: 0' : 'Product'}, inplace=True)

df = pd.melt(df, id_vars=['Product'], var_name='Period', value_name='Value')

df['Product'] = df['Product'].str.replace(r'([^a-zA-Z]+)', ' ')
df['Product'] = df['Product'].apply(lambda x: x.strip())

df['Period'] = df['Period'].map(lambda x: 'year/' + str(x))
df['Value'] = df['Value'].astype(str).astype(float).round(2)
df['Product'] = df['Product'].apply(pathify)
df = df[['Period', 'Product',  'Value']]

out = Path('out')
out.mkdir(exist_ok=True)
df.to_csv(out/'observations.csv', index = False)

# Metadata.json file is created manually as dataset was received as as raw csv file
with open('info.json') as f:
    info_json = json.load(f)
csvw_mapping = CSVWMapping()
csvw_mapping.set_mapping(info_json)
csvw_mapping.set_csv(out/'observations.csv')
csvw_mapping.set_dataset_uri(f"http://gss-data.org.uk/data/gss_data/climate-change/{info_json['id']}")
csvw_mapping.write(out/'observations.csv-metadata.json')

# metadata.trig file is manually created as dataset was received as as raw csv file
shutil.copy('observations.csv-metadata.trig', out/'observations.csv-metadata.trig')

