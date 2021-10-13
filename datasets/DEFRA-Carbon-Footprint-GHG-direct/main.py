#!/usr/bin/env python
# coding: utf-8

# In[7]:


import json
from gssutils import *
from pathlib import Path
import shutil
from gssutils.csvw.mapping import CSVWMapping

pd.set_option('display.float_format', lambda x: '%.1f' % x)

df = pd.read_csv("raw.csv")

df = pd.melt(df, id_vars=['Unnamed: 0'], var_name='Period', value_name='Value')

df = df.rename(columns = {'Unnamed: 0' : 'SIC Section'})

df = df.replace({'SIC Section' : {
    'Consumer expenditure - not travel' : 'http://business-data-gov-uk/companies/def/sic-2007/100',
    'Consumer expenditure - travel' : 'http://business-data-gov-uk/companies/def/sic-2007/101'
}})

df = df[['Period', 'SIC Section', 'Value']]

df['Period'] = df['Period'].map(lambda x: 'year/' + str(x))

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


# In[7]:




