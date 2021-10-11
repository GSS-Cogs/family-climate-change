#!/usr/bin/env python
# coding: utf-8

# In[164]:


import json
import pandas as pd
from gssutils import *

cubes = Cubes('info.json')
info = json.load(open('info.json'))

landingPage = info['landingPage']
landingPage


# In[165]:


scraper = Scraper(seed="info.json")
scraper


# In[166]:


distribution = scraper.distributions[0]

tabs = distribution.as_databaker(data_only=True)

tabs = [tab for tab in tabs if tab.name not in ['Contents', 'Summary']]
#Data contained in summary is present in other tabs

for i in tabs:
    print(i.name)


# In[167]:


dataframes = []

for tab in tabs:

    if tab.name not in "Aviation fuel":

        print(tab.name)

        pivot = tab.excel_ref("A1").shift(0, 4)

        remove = tab.filter("Notes").expand(DOWN).expand(RIGHT) | tab.filter("SIC (07) group") | tab.filter("Section")

        year = pivot.shift(3, 0).expand(RIGHT).is_not_blank()

        sicSection = tab.filter("Section").expand(DOWN) - remove #| tab.filter("SIC (07) group").expand(UP)) - remove

        sicGroup = tab.filter("SIC (07) group").expand(DOWN) - remove #| tab.filter("Section").expand(UP)) - remove

        industry = sicSection.shift(RIGHT).is_not_blank() - remove

        print(tab.name)

        if tab.name == 'Fuel oil':
            fueltype = 'Oil'
        elif tab.name == 'Gas oil':
            fueltype = 'Gas Oil Including Marine Oil Excluding DERV'
        else:
            fueltype = tab.name

        observations = industry.fill(RIGHT)

        dimensions = [
                HDim(year, 'Period', DIRECTLY, ABOVE),
                HDim(industry, 'Industry', DIRECTLY, LEFT),
                HDim(sicSection, 'SIC Section', DIRECTLY, LEFT),
                HDim(sicGroup, 'SIC Group', DIRECTLY, LEFT),
                HDimConst('Fuel', fueltype)
            ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        df = tidy_sheet.topandas()
        savepreviewhtml(tidy_sheet,fname=tab.name + "Preview.html")

        dataframes.append(df)

    elif tab.name == "Aviation fuel":

        print(tab.name)

        pivot = tab.excel_ref("A1").shift(0, 4)

        remove = tab.filter("Notes").expand(DOWN).expand(RIGHT) | tab.filter("SIC (07) group") | tab.filter("Section")

        year = pivot.shift(3, 0).expand(RIGHT).is_not_blank()

        sicSection = tab.filter("Section").expand(DOWN) - remove #| tab.filter("SIC (07) group").expand(UP)) - remove

        sicGroup = tab.filter("SIC (07) group").expand(DOWN) - remove #| tab.filter("Section").expand(UP)) - remove

        industry = sicSection.shift(RIGHT).is_not_blank() - remove

        fuel = industry.shift(RIGHT)

        observations = fuel.fill(RIGHT)

        dimensions = [
                HDim(year, 'Period', DIRECTLY, ABOVE),
                HDim(industry, 'Industry', DIRECTLY, LEFT),
                HDim(sicSection, 'SIC Section', DIRECTLY, LEFT),
                HDim(sicGroup, 'SIC Group', DIRECTLY, LEFT),
                HDim(fuel, 'Fuel', DIRECTLY, LEFT)
            ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        df = tidy_sheet.topandas()
        savepreviewhtml(tidy_sheet,fname=tab.name + "Preview.html")

        dataframes.append(df)


# In[168]:


df = pd.concat(dataframes)
df


# In[169]:


df = df.replace({'DATAMARKER' : {'c' : 'confidential'},
                 'Fuel' : {"('DERV',)" : 'DERV'}})

df['Period'] = df['Period'].astype(float).astype(int)

df['Period'] = df.apply(lambda x: 'year/' + str(x['Period']), axis = 1)

df['Measure Type'] = 'gross caloric values'

df['Unit'] = 'millions-of-tonnes-of-oil-equivalent'

df = df.rename(columns = {'DATAMARKER' : 'Marker', 'OBS' : 'Value'})

indexNames = df[ df['Industry'] == 'Total' ].index
df.drop(indexNames, inplace = True)

df['SIC Group'] = df.apply(lambda x: 'consumer-expenditure' if x['Industry'] == 'Consumer expenditure' else x['SIC Group'], axis = 1)

#df['SIC Group'] = df.apply(lambda x: pathify(x['SIC Group']), axis = 1)

#df['SIC Section'] = df.apply(lambda x: str(x['SIC Group']).replace('.', '-'), axis = 1)

title = 'ONS-E' + pathify(info['title'])[1:]

#info needed to create URI's for section
unique = 'http://gss-data.org.uk/data/gss_data/climate-change/' + title + '#concept/sic-2007/'
sic = 'http://business.data.gov.uk/companies/def/sic-2007/'

df['SIC Section'] = df.apply(lambda x: unique + pathify(x['SIC Group']) if x['SIC Group'][-2:] != '.0' else (sic + x['SIC Group'][:-2] if len(x['SIC Group']) != 3 else sic + '0' + x['SIC Group'][:-2]), axis = 1)

df['Fuel'] = df['Fuel'].fillna('all')

indexNames = df[ df['SIC Section'] == 'http://business.data.gov.uk/companies/def/sic-2007/' ].index
df.drop(indexNames, inplace = True)

indexNames = df[ df['SIC Section'] == 'http://gss-data.org.uk/data/gss_data/climate-change/ONS-Energy-use-fossil-fuels-by-fuel-type-and-industry#concept/sic-2007/' ].index
df.drop(indexNames, inplace = True)

df = df[['Period', 'SIC Section', 'Fuel', 'Value', 'Marker', 'Measure Type', 'Unit']]

COLUMNS_TO_NOT_PATHIFY = ['Period', 'Marker', 'Value', 'SIC Section']

for col in df.columns.values.tolist():
	if col in COLUMNS_TO_NOT_PATHIFY:
		continue
	try:
		df[col] = df[col].apply(pathify)
	except Exception as err:
		raise Exception('Failed to pathify column "{}".'.format(col)) from err

df


# In[170]:


scraper.dataset.title = info['title']
scraper.dataset.family = 'climate-change'
scraper.dataset.comment = info['description']

cubes.add_cube(scraper, df.drop_duplicates(), scraper.dataset.title)
cubes.output_all()


# In[171]:


from IPython.core.display import HTML
for col in df:
    if col not in ['Value']:
        df[col] = df[col].astype('category')
        display(HTML(f"<h2>{col}</h2>"))
        display(df[col].cat.categories)

