#!/usr/bin/env python
# coding: utf-8
# ## DEFRA-B3-State-of-the-water-environment
import pandas as pd
from gssutils import *

metadata = Scraper(seed="info.json")

metadata.select_dataset(title = lambda x: "State of the water environment" in x)

metadata.dataset.family = 'climate-change'

distribution = metadata.distribution(latest=True)

df = distribution.as_pandas(encoding='ISO-8859-1')

# +
df['Label'] = df['Year'].str.extract(r'([^(\d+)]+)')
df['Year'] = df['Year'].str.extract(r'(\d+)')

df['Region'] = 'E92000001'

df['Year'] = df.apply(lambda x: '2019' if 'B3a' in x['Series'] else ('2019' if 'B3b' in x['Series'] else x['Year']), axis = 1)
df['Year'] = df.apply(lambda x: 'year/' + x['Year'], axis = 1)

df['Measure Type'] = df.apply(lambda x: 'status-of-surface-waters' if 'B3a' in x['Series'] else '', axis = 1)
df['Measure Type'] = df.apply(lambda x: 'status-of-ground-waters' if 'B3b' in x['Series'] else x['Measure Type'], axis = 1)
df['Measure Type'] = df.apply(lambda x: 'status-of-waters-specially-protected-for-specific-uses' if 'B3c' in x['Series'] else x['Measure Type'], axis = 1)

df['Unit'] = df.apply(lambda x: 'percentage-of-area' if 'B3c' in x['Series'] else 'percentage-of-water-bodies-assessed', axis = 1)
df = df.rename(columns={'Year' : 'Period', 'Label' : 'Environment Surveyed', 'Component' : 'Survey Type', 'Status category' : 'Survey Status', 'Measure Type' : 'Measure'})


df['Survey Type'] = df.apply(lambda x: 'ecological-status' if 'B3b' in x['Series'] else x['Survey Type'], axis = 1)

df = df.drop(['Series'], axis = 1)
df = df[['Period', 'Region', 'Environment Surveyed', 'Survey Type', 'Survey Status', 'Measure', 'Unit', 'Value']]
df = df.fillna('not available')

# +
COLUMNS_TO_NOT_PATHIFY = ['Period', 'Region', 'Value']

for col in df.columns.values.tolist():
	if col in COLUMNS_TO_NOT_PATHIFY:
		continue
	try:
		df[col] = df[col].apply(pathify)
	except Exception as err:
		raise Exception('Failed to pathify column "{}".'.format(col)) from err	
# -

df.to_csv('observations.csv', index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')
