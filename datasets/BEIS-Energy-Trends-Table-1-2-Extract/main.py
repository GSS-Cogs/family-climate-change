#!/usr/bin/env python
# coding: utf-8
import pandas as pd
from gssutils import *

metadata = Scraper(seed='info.json')

# +

distribution = metadata.distribution(title = lambda x: "Energy Trends total energy table(ODS) in x, metaType = (ODF Spreadsheet)",latest=True)


# +
df = pd.read_csv("Energy Trends 1.2 IDP Extract.csv")

df = df[:-5]
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

df = pd.melt(df, id_vars = ['Year'], var_name = 'Fuel', value_name = 'Value', ignore_index = True)

df = df.rename(columns={'Year' : 'Period'})

df['Period'] = df.apply(lambda x: 'year/' + str(x['Period'])[:-2], axis = 1)

df['Region'] = 'K02000001'

df['Measure Type'] = 'Energy Consumption'

df['Unit'] = 'Millions of Tonnes of Oil Equivalent'

df = df[['Period', 'Region', 'Fuel', 'Measure Type', 'Unit', 'Value']]


# +
COLUMNS_TO_NOT_PATHIFY = ['Value', 'Period', 'Region', 'Marker']

for col in df.columns.values.tolist():
	if col in COLUMNS_TO_NOT_PATHIFY:
		continue
	try:
		df[col] = df[col].apply(pathify)
	except Exception as err:
		raise Exception('Failed to pathify column "{}".'.format(col)) from err

df = df.replace({'Fuel' : {'-natural-gas' : 'natural-gas','total' : 'all','biogenergy-and-waste' : 'bioenergy-and-waste'}})
# -


df.to_csv('observations.csv', index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')
