#!/usr/bin/env python
# coding: utf-8

# In[137]:


# ## BEIS-Sub-national-road-transport-fuel-consumption-in-the-United-Kingdom

import json
import pandas as pd
from gssutils import *

pd.set_option('display.float_format', lambda x: '%.1f' % x)

cubes = Cubes('info.json')
info = json.load(open('info.json'))
landingPage = info['landingPage']
metadata = Scraper(seed='info.json')
distribution = metadata.distribution(title = lambda x: "Sub-national road transport fuel consumption statistics, 2005-2019 (Excel)" in x, latest = True)
tabs = distribution.as_databaker()
title = metadata.title


# In[138]:


tidied_sheets = []
for tab in tabs[2:-1]:

    print(tab.name)

    pivot = tab.excel_ref('A5')

    LACode = pivot.fill(DOWN)
    transport = pivot.shift(3,0).expand(RIGHT)
    geography = LACode.shift(RIGHT)

    observations = transport.fill(DOWN).is_not_blank()

    dimensions = [
                HDimConst('Period', tab.name),
                HDim(LACode, 'Local Authority Code', DIRECTLY, LEFT),
                HDim(geography, 'Geography', DIRECTLY, LEFT),
                HDim(transport, 'Transport', DIRECTLY, ABOVE)
            ]

    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    df = tidy_sheet.topandas()
    savepreviewhtml(tidy_sheet,fname=tab.name + "Preview.html")

    tidied_sheets.append(df)


# In[139]:


df = pd.concat(tidied_sheets, sort=True)
df.rename(columns={'OBS' : 'Value'}, inplace=True)

df['Local Authority Code'] = df.apply(lambda x: x['Geography'] if x['Local Authority Code'] == '' else x['Local Authority Code'], axis = 1)

df['Transport'] = df['Transport'].str.replace('\n', '')

df['Road Type'] = df.apply(lambda x: x['Transport'].split('-')[1].strip() if '-' in x['Transport'] else 'all', axis = 1)

df['Vehicle'] = df.apply(lambda x: x['Transport'].split('-')[0].strip() if '-' in x['Transport'] else x['Transport'], axis = 1)

df['Purpose'] = df['Transport'].map(lambda x: 'Freight' if 'GV' in x else ('all' if 'All vehicles' in x else 'Personal'))

df['Vehicle']  = df['Vehicle'].str.replace('total', '').str.strip()

df = df.replace({'Local Authority Code' : {'Wales' : 'W92000004',
                                           'Scotland' : 'S92000003',
                                           'England' : 'E92000001',
                                           'Northern Ireland' : 'N92000002'},
                 'Vehicle' : {'Freight transport (HGV and LGV)[Note 4] [Note 5]' : 'All Freight',
                              'Personal transport (buses, cars and motorcycles)' : 'All Personal',
                              'All vehicles' : 'all'}})

df['Period'] = 'year/' + df['Period']

df = df.drop(['Geography', 'Transport'], axis = 1)

df = df.rename(columns = {'Local Authority Code' : 'Region'})

df['Value'] = df['Value'].round(2)

df = df[['Period', 'Region', 'Road Type', 'Vehicle', 'Purpose', 'Value']]

COLUMNS_TO_NOT_PATHIFY = ['Period', 'Region', 'Value']

for col in df.columns.values.tolist():
	if col in COLUMNS_TO_NOT_PATHIFY:
		continue
	try:
		df[col] = df[col].apply(pathify)
	except Exception as err:
		raise Exception('Failed to pathify column "{}".'.format(col)) from err

df


# In[140]:


cubes.add_cube(metadata, df.drop_duplicates(), title)
cubes.output_all()


# In[140]:




