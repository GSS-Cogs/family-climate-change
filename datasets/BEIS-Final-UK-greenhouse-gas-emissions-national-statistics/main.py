#!/usr/bin/env python
# coding: utf-8

# In[182]:


from gssutils import *

cubes = Cubes("info.json")

scraper = Scraper(seed = "info.json")
scraper


# In[183]:


distribution  = scraper.distribution(latest=True, title = lambda x:"2020 UK greenhouse gas emissions: provisional figures - data tables" in x)
distribution


# In[184]:


tabs = distribution.as_databaker()

for tab in tabs:
    print(tab.name)


# In[185]:


sheets = []

tabs = [tab for tab in tabs if 'Contents' not in tab.name]

for tab in tabs:

    if tab.name not in ['Table 3', 'Table 4']: #tables 3 and 4 are moving averages

        remove = tab.filter(contains_string("2020 estimates")).expand(RIGHT).expand(DOWN)

        cell = tab.excel_ref("A2")

        if tab.name not in ['Table 1', 'Table 2']:
            period = cell.fill(RIGHT).is_not_blank().is_not_whitespace()
            quarter = period.shift(DOWN).expand(RIGHT)
        else:
            period = cell.fill(RIGHT).is_not_blank().is_not_whitespace()
            quarter = period

        area = 'K02000001'

        if tab.name not in ['Table 2']:
            ncSector = cell.fill(DOWN).is_not_blank().is_not_whitespace() - remove
            fuel = 'all'
        else:
            ncSector = 'all'
            fuel = cell.fill(DOWN).is_not_blank().is_not_whitespace() - remove

        if tab.name in ['Table 1', 'Table 5']:
            measureType = 'greenhouse-gas-emissions'
            unit = 'millions-of-tonnes-of-co2-equivalent'
        elif tab.name in ['Table 2']:
            measureType  = 'carbon-dioxide-emissions'
            unit = 'millions-of-tonnes-of-co2'
        elif tab.name in ['Table 6']:
            measureType  = 'temperature-adjusted-greenhouse-gas-emissions'
            unit = 'millions-of-tonnes-of-co2-equivalent'

        observations = quarter.fill(DOWN).is_not_blank().is_not_whitespace() - remove

        if tab.name not in ['Table 2']:
            dimensions = [
                HDimConst('Area', area),
                HDim(period, "Period", CLOSEST, LEFT),
                HDim(quarter, "Quarter", DIRECTLY, ABOVE),
                HDim(ncSector, "National Communication Sector", DIRECTLY, LEFT),
                HDimConst('Fuel', fuel),
                HDimConst('Measure Type', measureType),
                HDimConst('Unit', unit)
            ]
        else:
            dimensions = [
                HDimConst('Area', area),
                HDim(period, "Period",  CLOSEST, LEFT),
                HDim(quarter, "Quarter", DIRECTLY, ABOVE),
                HDimConst("National Communication Sector", ncSector),
                HDim(fuel, 'Fuel', DIRECTLY, LEFT),
                HDimConst('Measure Type', measureType),
                HDimConst('Unit', unit)
            ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        df = tidy_sheet.topandas()
        savepreviewhtml(tidy_sheet,fname=tab.name + "Preview.html")

        sheets.append(df)


# In[186]:


df = pd.concat(sheets)

df['Marker'] = df.apply(lambda x: 'provisional' if '(p)' in x['Period'] else '', axis = 1)
df['Period'] = df.apply(lambda x: 'year/' + str(x['Period'])[:4] if 'Q' not in x['Quarter']                                                                 else 'quarter/' + str(x['Period'])[:4] + '-' + str(x['Quarter']), axis = 1)
df = df.drop(columns = ['Quarter'])

df = df.replace({'National Communication Sector' : {'     from power stations' : 'Power Stations',
                                 '     other Energy supply' : 'Other Energy Supply',
                                                    'lulucf' : 'land-use-land-use-change-and-forestry'}})

indexNames = df[ df['Fuel'] == 'Total' ].index
df.drop(indexNames, inplace = True)

df['National Communication Sector'] = df['National Communication Sector'].map(lambda x: pathify(x))
df['Fuel'] = df['Fuel'].map(lambda x: pathify(x))

df = df.rename(columns = {'OBS' : 'Value'})

df = df[['Period', 'Area', 'National Communication Sector', 'Fuel', 'Value', 'Marker', 'Measure Type', 'Unit']]

df


# In[187]:


scraper.dataset.comment = """Final estimates of UK territorial greenhouse gas emissions, including provisional data for 2020"""

cubes.add_cube(scraper, df.drop_duplicates(), scraper.dataset.title)
cubes.output_all()


# In[187]:




