#!/usr/bin/env python
# coding: utf-8

# In[118]:


import json
from gssutils import *
from pathlib import Path
import shutil
from gssutils.csvw.mapping import CSVWMapping

#pd.set_option('display.float_format', lambda x: '%.1f' % x)

df = pd.read_csv("raw.csv", header = 2)
df


# In[119]:


dfGHG = df.truncate(after = 28)

dfGHG = dfGHG.drop(columns = ['Unnamed: 0'])

dfGHG = pd.melt(dfGHG, id_vars=['Unnamed: 1'], var_name='Product', value_name='Value')

dfGHG['Measure Type'] = 'greenhouse-gas-emissions'
dfGHG['Unit'] = 'KT-CO2e'

dfGHG


# In[120]:


dfCO = df.truncate(before = 33, after = 61)

dfCO = dfCO.drop(columns = ['Unnamed: 0'])

dfCO = pd.melt(dfCO, id_vars=['Unnamed: 1'], var_name='Product', value_name='Value')

dfCO['Measure Type'] = 'carbon-dioxide-emissions'
dfCO['Unit'] = 'KT-CO2'

dfCO


# In[121]:


dfNRG = df.truncate(before = 66)

dfNRG = dfNRG.drop(columns = ['Unnamed: 0'])

dfNRG = pd.melt(dfNRG, id_vars=['Unnamed: 1'], var_name='Product', value_name='Value')

dfNRG['Measure Type'] = 'energy'
dfNRG['Unit'] = 'KT-oil-equivalent'

dfNRG


# In[122]:


df = pd.concat([dfGHG, dfCO, dfNRG])

df = df.rename(columns = {'Unnamed: 1' : 'Period'})

df['Period'] = df['Period'].astype(float).astype(int)

df['Period'] = df['Period'].map(lambda x: 'year/' + str(x))

df = df.replace({'Product' : {'Total' : 'All'}})

df['Unit'] = df['Unit'].map(lambda x: pathify(x))

df


# In[123]:


out = Path('out')
out.mkdir(exist_ok=True)
df.to_csv(out/'observations.csv', index = False)

# ## No scraper present so we have created this manually

# +
with open('info.json') as f:
    info_json = json.load(f)
csvw_mapping = CSVWMapping()
csvw_mapping.set_mapping(info_json)
csvw_mapping.set_csv(out/"observations.csv")
csvw_mapping.set_dataset_uri(f"http://gss-data.org.uk/data/gss_data/climate-change/{info_json['id']}")
csvw_mapping.write(out/'observations.csv-metadata.json')

shutil.copy("observations.csv-metadata.trig", out/"observations.csv-metadata.trig")

#%#

