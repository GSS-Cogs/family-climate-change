#!/usr/bin/env python
# coding: utf-8

# In[3]:


import json
import pandas as pd
from gssutils import *

cubes = Cubes('info.json')
info = json.load(open('info.json'))

landingPage = info['landingPage']
landingPage


# In[4]:


metadata = Scraper(seed='info.json')

metadata.select_dataset(title = lambda x: 'E8' in x)

distribution = metadata.distribution(mediaType="text/csv")
metadata.dataset.title = distribution.title
metadata.dataset.family = 'DEFRA'

df = distribution.as_pandas()

df['Year'] = df['Year'].str.replace(r'-', r'-20')

df['Year'] = df.apply(lambda x: 'government-year/+' + x['Year'], axis = 1)

df = df.rename({'Year' : 'Period'})

df['Unit'] = df.apply(lambda x: 'megalitres-per-day' if 'E8A' in x['Series'] else 'litres-per-person-per-day', axis = 1)
df['Measure Type'] = df.apply(lambda x: 'water-leakage' if 'E8A' in x['Series'] else 'water-consumption', axis = 1)

df = df.drop(['Series'])

df['Value'] = pd.to_numeric(df['Value'], downcast='float')
df['Value'] = df['Value'].astype(str).astype(float).round(2)
df = df.fillna('not available')

#df['Series'] = df['Series'].apply(pathify)

cubes.add_cube(metadata, df.drop_duplicates(), metadata.dataset.title)
cubes.output_all()

