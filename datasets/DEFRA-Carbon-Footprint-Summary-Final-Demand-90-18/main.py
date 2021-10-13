#!/usr/bin/env python
# coding: utf-8

# In[44]:


import json
from gssutils import *
from pathlib import Path
import shutil
from gssutils.csvw.mapping import CSVWMapping

pd.set_option('display.float_format', lambda x: '%.4f' % x)

df = pd.read_csv("Summary_final_demand_90-18.csv", header = 2)

df = df.iloc[: , 1:]

df = df.rename(columns={'Unnamed: 1' : 'Period', 'Unnamed: 10' : 'Total', 'Non-profit\ninstitutions serving\nhouseholds' : 'Non-profit institutions serving households', 'Gross fixed\ncapital\nformation' : 'Gross fixed capital formation'})

df = pd.melt(df, id_vars=['Period'], var_name='Final Demand Breakdown', value_name='Value')

df['Final Demand'] = df['Final Demand Breakdown']

df = df.replace({'Final Demand' : {'Households' : 'FD1',
                                   'Households direct' : 'FD1',
                                   'Non-profit institutions serving households' : 'FD2',
                                   'Central Government' : 'FD3',
                                   'Local Government' : 'FD4',
                                   'Gross fixed capital formation' : 'FD5',
                                   'Valuables' : 'FD6',
                                   'Changes in inventories' : 'FD7',
                                   'Total' : 'all'},
                 'Final Demand Breakdown' : {'Total' : 'all'}})

df = df[['Period', 'Final Demand', 'Final Demand Breakdown', 'Value']]

df['Period'] = df['Period'].map(lambda x: 'year/' + str(x))

df['Final Demand Breakdown'] = df['Final Demand Breakdown'].map(lambda x: pathify(x))

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


# In[44]:




