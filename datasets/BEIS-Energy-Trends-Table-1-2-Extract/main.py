#!/usr/bin/env python
# coding: utf-8

# In[397]:


from IPython.display import display

from gssutils import *
import json
import re

cubes = Cubes("info.json")
info = json.load(open('info.json'))


# In[398]:


scraper = Scraper(seed='info.json')
scraper


# In[399]:


dist = [x for x in scraper.distributions if '1.2' in x.title][0]
dist


# In[400]:


excluded = ['Contents', 'Highlights', 'Calculation']

tabs = [x for x in dist.as_databaker() if x.name not in excluded and 'Main table' not in x.name]
#"Main Table" tabs are built from annual and month tabs

for tab in tabs:
    print(tab.name)


# In[401]:


tidied_sheets = {}

for tab in tabs:

    print(tab.name)

    pivot = tab.filter('Year')

    remove = tab.filter("Return to contents page").expand(RIGHT).expand(DOWN)

    year = pivot.fill(DOWN).is_not_blank() - remove

    if 'Annual' in tab.name:
        yearBreakdown = year
    elif 'Quarter' in tab.name or 'Month' in tab.name:
        yearBreakdown = year.shift(RIGHT)

    seasonalAdjustment = pivot.shift(DOWN).expand(RIGHT).is_not_blank()

    fuel = pivot.shift(2, 0).expand(RIGHT).is_not_blank()

    measure = 'Energy Consumption'

    unit = 'Millions of Tonnes of Oil Equivalent'

    observations = yearBreakdown.shift(RIGHT).expand(RIGHT).is_not_blank() - remove

    dimensions = [
            HDim(year, 'Period', CLOSEST, ABOVE),
            HDim(yearBreakdown, 'yearBreakdown', DIRECTLY, LEFT),
            HDim(seasonalAdjustment, 'Seasonal Adjustment', CLOSEST, LEFT),
            HDim(fuel, 'Fuel', DIRECTLY, ABOVE),
            HDimConst('Area', 'K02000001'),
            HDimConst('Measure Type', measure),
            HDimConst('Unit', unit)
    ]

    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    savepreviewhtml(tidy_sheet, fname=tab.name + "Preview.html")
    tidied_sheets[tab.name] = tidy_sheet.topandas()


# In[402]:


df = pd.concat(tidied_sheets.values())

df['Period'] = df.apply(lambda x: 'year/' + x['Period'][:-2] if x['Period'] == x['yearBreakdown'] else x['Period'], axis = 1)
df['Period'] = df.apply(lambda x: 'quarter/'+ x['Period'][:-2] + '-Q' + x['yearBreakdown'].replace('Quarter ', '') if 'Quarter' in x['yearBreakdown'] else x['Period'], axis = 1)

df['yearBreakdown'] = df['yearBreakdown'].str.replace('*', '').str.strip()
df['yearBreakdown']  = df.apply(lambda x: x['yearBreakdown'][:-1].strip() if x['yearBreakdown'][-2] == ' r' else x['yearBreakdown'], axis = 1)
#return to this when attribute comments are fully implemented

df = df.replace({'yearBreakdown' : {'January' : '01',
                                    'February' : '02',
                                    'March' : '03',
                                    'April' : '04',
                                    'May' : '05',
                                    'June' : '06',
                                    'July' : '07',
                                    'August' : '08',
                                    'September' : '09',
                                    'October' : '10',
                                    'November' : '11',
                                    'December' : '12'},
                 'Fuel' : {' gas' : 'Natural Gas',
                           ' imports' : 'Net Imports',
                           '& waste' : 'Bioenergy and waste',
                           'Total' : 'All',
                           'and hydro' : 'wind solar and energy',
                           'gas' : 'Natural Gas'},
                 'Seasonal Adjustment' : {'Seasonally adjusted and temperature corrected(annualised rates)' : 'Seasonally adjusted and temperature corrected (annualised rates)'},
                 'DATAMARKER' : {'n/a' : 'not-available'}})

df['Period'] = df.apply(lambda x: 'month/' + x['Period'][:-2] + '-' + x['yearBreakdown'] if len(x['yearBreakdown']) == 2 else x['Period'], axis = 1)

df['OBS'] = df.apply(lambda x: round(float(x['OBS']), 2) if x['DATAMARKER'] != 'not-available' else x['OBS'], axis = 1)

df = df.drop(columns = ['yearBreakdown'])

df = df.rename(columns={'OBS' : 'Value', 'Area' : 'Region', 'DATAMARKER' : 'Marker'})

COLUMNS_TO_NOT_PATHIFY = ['Value', 'Period', 'Region', 'Marker']

for col in df.columns.values.tolist():
	if col in COLUMNS_TO_NOT_PATHIFY:
		continue
	try:
		df[col] = df[col].apply(pathify)
	except Exception as err:
		raise Exception('Failed to pathify column "{}".'.format(col)) from err

df


# In[403]:


scraper.dataset.family = 'climate-change'
scraper.dataset.comment = """
An overview of the trends in energy production and consumption in the United Kingdom for the previous quarter, focusing on: consumption, both primary and final by broad sector, including seasonally adjusted series
"""
scraper.dataset.contactPoint = "energy.stats@beis.gov.uk"

csvName = 'observations'
cubes.add_cube(scraper, df.drop_duplicates(), csvName)


# In[404]:


cubes.output_all()


# In[405]:


from IPython.core.display import HTML
for col in df:
    if col not in ['Value']:
        df[col] = df[col].astype('category')
        display(HTML(f"<h2>{col}</h2>"))
        display(df[col].cat.categories)


# In[405]:




