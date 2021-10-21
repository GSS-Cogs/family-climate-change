#!/usr/bin/env python
# coding: utf-8

# In[ ]:



import pandas as pd
from IPython.display import display

from gssutils import *
import json
import re

cubes = Cubes("info.json")
info = json.load(open('info.json'))


# In[ ]:



scraper = Scraper(seed='info.json')
scraper


# In[ ]:



dist = [x for x in scraper.distributions if '1.2' in x.title][0]
dist


# In[ ]:



df = pd.read_csv("Energy Trends 1.2 IDP Extract.csv")

df = df[:-5]
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

df = pd.melt(df, id_vars = ['Year'], var_name = 'Fuel', value_name = 'Value', ignore_index = True)

df = df.rename(columns={'Year' : 'Period'})

df


# In[ ]:



df['Period'] = df.apply(lambda x: 'year/' + str(x['Period'])[:-2], axis = 1)

df['Region'] = 'K02000001'

df['Measure Type'] = 'Energy Consumption'

df['Unit'] = 'Millions of Tonnes of Oil Equivalent'

df = df[['Period', 'Region', 'Fuel', 'Value', 'Measure Type', 'Unit']]

COLUMNS_TO_NOT_PATHIFY = ['Value', 'Period', 'Region', 'Marker']

for col in df.columns.values.tolist():
	if col in COLUMNS_TO_NOT_PATHIFY:
		continue
	try:
		df[col] = df[col].apply(pathify)
	except Exception as err:
		raise Exception('Failed to pathify column "{}".'.format(col)) from err

df = df.replace({'Fuel' : {'-natural-gas' : 'natural-gas',
                           'total' : 'all',
                           'biogenergy-and-waste' : 'bioenergy-and-waste'}})

df


# In[ ]:



scraper.dataset.title = dist.title
scraper.dataset.family = 'climate-change'
scraper.dataset.comment = """
An overview of the trends in energy production and consumption in the United Kingdom for the previous quarter, focusing on: consumption, both primary and final by broad sector, including seasonally adjusted series
"""
scraper.dataset.contactPoint = "energy.stats@beis.gov.uk"

csvName = 'observations'
cubes.add_cube(scraper, df.drop_duplicates(), csvName)


# In[ ]:


cubes.output_all()


# In[ ]:



from IPython.core.display import HTML
for col in df:
    if col not in ['Value']:
        df[col] = df[col].astype('category')
        display(HTML(f"<h2>{col}</h2>"))
        display(df[col].cat.categories)


# In[ ]:




