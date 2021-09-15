#!/usr/bin/env python
# coding: utf-8

# In[1]:


# ## DEFRA-B3-State-of-the-water-environment

import json
import pandas as pandas
from gssutils import *

cubes = Cubes('info.json')
info = json.load(open('info.json'))
landingPage = info['landingPage']
landingPage


# In[ ]:


metadata = Scraper(seed="info.json")
metadata.select_dataset(title = lambda x: "B3" in x)

distribution = metadata.distribution(mediaType="text/csv")

metadata.dataset.title = info['title']
metadata.dataset.family = 'climate-change'
metadata.dataset.comment = info['description']

df = distribution.as_pandas()

df['Label'] = df['Year'].str.extract(r'([^(\d+)]+)')
df['Year'] = df['Year'].str.extract(r'(\d+)')

df['Area'] = 'E92000001'

df['Year'] = df.apply(lambda x: '2019' if 'B3a' in x['Series'] else ('2019' if 'B3b' in x['Series'] else x['Year']), axis = 1)
df['Year'] = df.apply(lambda x: 'year/' + x['Year'], axis = 1)

df['Measure Type'] = df.apply(lambda x: 'status-of-surface-waters' if 'B3a' in x['Series'] else '', axis = 1)
df['Measure Type'] = df.apply(lambda x: 'status-of-ground-waters' if 'B3b' in x['Series'] else x['Measure Type'], axis = 1)
df['Measure Type'] = df.apply(lambda x: 'status-of-waters-specially-protected-for-specific-uses' if 'B3c' in x['Series'] else x['Measure Type'], axis = 1)

df['Unit'] = df.apply(lambda x: 'percentage-of-area' if 'B3c' in x['Series'] else 'percentage-of-water-bodies-assessed', axis = 1)

#these measures and units seem a little verbose to me and could probably be changed in conjunction with an attribute or something
#but these are taken directly from the landing page so they'll do for now

df = df.rename(columns={'Year' : 'Period', 'Label' : 'Environment Surveyed', 'Component' : 'Survey Type', 'Status category' : 'Survey Status'})

#Could probably do with better column headers but I couldnt think of anything better at the moment

df['Survey Type'] = df.apply(lambda x: 'ecological-status' if 'B3b' in x['Series'] else x['Survey Type'], axis = 1)

df = df.drop(['Series'], axis = 1)


# In[ ]:


df = df[['Period', 'Area', 'Environment Surveyed', 'Survey Type', 'Survey Status', 'Value', 'Measure Type', 'Unit']]
df = df.fillna('not available')


# In[ ]:


COLUMNS_TO_NOT_PATHIFY = ['Period', 'Area', 'Value']

for col in df.columns.values.tolist():
	if col in COLUMNS_TO_NOT_PATHIFY:
		continue
	try:
		df[col] = df[col].apply(pathify)
	except Exception as err:
		raise Exception('Failed to pathify column "{}".'.format(col)) from err


# In[ ]:


cubes.add_cube(metadata, df.drop_duplicates(), metadata.dataset.title)
cubes.output_all()

