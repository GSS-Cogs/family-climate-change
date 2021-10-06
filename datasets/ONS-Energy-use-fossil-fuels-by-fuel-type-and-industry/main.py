#!/usr/bin/env python
# coding: utf-8

# In[130]:


import json
import pandas as pd
from gssutils import *

cubes = Cubes('info.json')
info = json.load(open('info.json'))

landingPage = info['landingPage']
landingPage


# In[131]:


scraper = Scraper(seed="info.json")
scraper


# In[132]:


distribution = scraper.distributions[0]

tabs = distribution.as_databaker(data_only=True)

tabs = [tab for tab in tabs if tab.name not in ['Contents', 'Summary']]
#Data contained in summary is present in other tabs

for i in tabs:
    print(i.name)


# In[133]:


dataframes = []

for tab in tabs:

    if tab.name not in "Aviation fuel":

        print(tab.name)

        pivot = tab.excel_ref("A1").shift(0, 4)

        remove = tab.filter("Notes").expand(DOWN).expand(RIGHT) | tab.filter("SIC (07) group") | tab.filter("Section")

        year = pivot.shift(3, 0).expand(RIGHT).is_not_blank()

        industry = pivot.shift(2, 0).expand(DOWN).is_not_blank() - remove

        sicSection = (tab.filter("Section").expand(DOWN) | tab.filter("SIC (07) group").expand(UP)) - remove

        sicGroup = (tab.filter("SIC (07) group").expand(DOWN) | tab.filter("Section").expand(UP)) - remove

        print(tab.name)

        if tab.name == 'Fuel oil':
            fueltype = 'Oil'
        elif tab.name == 'Gas oil':
            fueltype = 'Gas Oil Including Marine Oil Excluding DERV'
        else:
            fueltype = tab.name

        observations = year.fill(DOWN) & industry.fill(RIGHT)

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

        industry = pivot.shift(2, 0).expand(DOWN).is_not_blank() - remove

        sicSection = (tab.filter("Section").expand(DOWN) | tab.filter("SIC (07) group").expand(UP)) - remove

        sicGroup = (tab.filter("SIC (07) group").expand(DOWN) | tab.filter("Section").expand(UP)) - remove

        fuel = industry.shift(RIGHT)

        observations = year.fill(DOWN) & industry.fill(RIGHT)

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


# In[134]:


df = pd.concat(dataframes)

df = df.replace({'DATAMARKER' : {'c' : 'confidential'},
                 'Fuel' : {"('DERV',)" : 'DERV'}})

df['Period'] = df['Period'].astype(float).astype(int)

df['Period'] = df.apply(lambda x: 'year/' + str(x['Period']), axis = 1)

#df['Measure Type'] = 'gross caloric values'

#df['Unit'] = 'millions-of-tonnes-of-oil-equivalent'

df = df.rename(columns = {'DATAMARKER' : 'Marker', 'OBS' : 'Value'})

indexNames = df[ df['Industry'] == 'Total' ].index
df.drop(indexNames, inplace = True)

df['SIC Group'] = df.apply(lambda x: 'consumer-expenditure' if x['Industry'] == 'Consumer expenditure' else x['SIC Group'], axis = 1)

df['SIC Group'] = df.apply(lambda x: pathify(x['SIC Group']), axis = 1)

df['SIC Section'] = df.apply(lambda x: str(x['SIC Group']).replace('.', '-') if x['SIC Group'] != '' else x['SIC Section'], axis = 1)

title = 'ONS-E' + pathify(info['title'])[1:]

#info needed to create URI's for section
unique = 'http://gss-data.org.uk/data/gss_data/climate-change/' + title + '#concept/sic-2007/'
sic = 'http://business.data.gov.uk/companies/def/sic-2007/'
#create the URI's from the section column
df['SIC Section'] = df['SIC Section'].map(lambda x: unique + x if '-' in x else sic + x)
#only need the following columns

df['Fuel'] = df['Fuel'].fillna('all')

indexNames = df[ df['SIC Section'] == 'http://business.data.gov.uk/companies/def/sic-2007/' ].index
df.drop(indexNames, inplace = True)

#df = df[['Period', 'SIC Section', 'Fuel', 'Value', 'Marker']]

COLUMNS_TO_NOT_PATHIFY = ['Period', 'Marker', 'Value', 'SIC Section']

for col in df.columns.values.tolist():
	if col in COLUMNS_TO_NOT_PATHIFY:
		continue
	try:
		df[col] = df[col].apply(pathify)
	except Exception as err:
		raise Exception('Failed to pathify column "{}".'.format(col)) from err

df


# In[135]:


scraper.dataset.title = info['title']
scraper.dataset.family = 'climate-change'
scraper.dataset.comment = info['description']

cubes.add_cube(scraper, df.drop_duplicates(), scraper.dataset.title)
cubes.output_all()


# In[136]:


from IPython.core.display import HTML
for col in df:
    if col not in ['Value']:
        df[col] = df[col].astype('category')
        display(HTML(f"<h2>{col}</h2>"))
        display(df[col].cat.categories)

