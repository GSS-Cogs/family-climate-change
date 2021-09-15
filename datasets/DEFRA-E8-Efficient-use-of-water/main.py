#!/usr/bin/env python
# coding: utf-8

# In[1]:


import json
import pandas as pd
from gssutils import *

cubes = Cubes('info.json')
info = json.load(open('info.json'))

landingPage = info['landingPage']
landingPage


# In[2]:


metadata = Scraper(seed='info.json')

metadata.select_dataset(title = lambda x: 'E8' in x)

distribution = metadata.distribution(mediaType="text/csv")

metadata.dataset.title = info['title']
metadata.dataset.family = 'climate-change'
metadata.dataset.comment = info['description']

df = distribution.as_pandas()

df['Year'] = df['Year'].str.replace(r'-', r'-20')

df['Year'] = df.apply(lambda x: 'government-year/' + x['Year'], axis = 1)

df = df.rename(columns={'Year' : 'Period'})

df['Measure Type'] = df.apply(lambda x: 'water-leakage' if 'E8b' in x['Series'] else 'water-consumption', axis = 1)
df['Unit'] = df.apply(lambda x: 'megalitres-per-day' if 'E8b' in x['Series'] else 'litres-per-person-per-day', axis = 1)

df = df.drop(['Series'], axis = 1)

df['Value'] = pd.to_numeric(df['Value'], downcast='float')
df['Value'] = df['Value'].astype(str).astype(float).round(2)
df = df.fillna('not available')

df['Marker'] = df.apply (lambda x: 'not-available' if 'not available' in str(x['Value']) else '', axis = 1)
df['Value'] = df.apply (lambda x: 0 if 'not available' in str(x['Value']) else x['Value'], axis = 1)

#df['Series'] = df['Series'].apply(pathify)

cubes.add_cube(metadata, df.drop_duplicates(), metadata.dataset.title)
cubes.output_all()

