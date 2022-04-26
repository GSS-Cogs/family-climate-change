#!/usr/bin/env python
# coding: utf-8
# ## BEIS-Provisional-UK-greenhouse-gas-emissions-national-statistics-2021

import json
import pandas as pd
from gssutils import *

metadata = Scraper(seed="info.json")

distribution = metadata.distribution(
    latest=True, mediaType="application/vnd.oasis.opendocument.spreadsheet", title=lambda x: "UK greenhouse gas emissions: provisional figures - data tables" in x)

tabs = distribution.as_databaker()

sheets = []
tabs = [tab for tab in tabs if tab.name not in ['Cover', 'Contents', 'Notes']]
for tab in tabs:

    if tab.name not in ['Table3', 'Table4']:  # tables 3 and 4 are moving averages
        if tab.name not in ['Table2']:
            ncSector = tab.filter("NC Sector").fill(DOWN).is_not_blank()
            fuel = 'all'
            period = tab.filter("NC Sector").fill(RIGHT).is_not_blank()
        else:
            sector = tab.filter('Sector').fill(DOWN).is_not_blank()
            fuel = tab.filter('Fuel Type').fill(DOWN).is_not_blank()
            period = tab.filter('Fuel Type').fill(RIGHT).is_not_blank()

        if tab.name in ['Table1', 'Table5']:
            measureType = 'greenhouse-gas-emissions'
            
        elif tab.name == 'Table2':
            measureType = 'carbon-dioxide-emissions'

        elif tab.name in ['Table6']:
            measureType = 'temperature-adjusted-greenhouse-gas-emissions'
        
        elif tab.name in ['AR5_Table1']:
            measureType = 'greenhouse-gas-emissions (GWP AR5)'
            
        else:
            continue

        area = 'K02000001'
        observations = period.fill(DOWN).is_not_blank()
        unit = 'millions-of-tonnes-of-co2-equivalent'

        if tab.name not in ['Table2']:
            dimensions = [
                HDim(period, "Period", CLOSEST, LEFT),
                HDim(ncSector, "National Communication Sector", DIRECTLY, LEFT),
                HDimConst('Area', area),
                HDimConst('Fuel', fuel),
                HDimConst('Measure', measureType),
                HDimConst('Unit', unit)
            ]
        else:
            dimensions = [
                HDim(period, "Period",  CLOSEST, LEFT),
                HDim(fuel, 'Fuel', DIRECTLY, LEFT),
                HDim(sector, "National Communication Sector", CLOSEST, ABOVE),
                HDimConst('Area', area),
                HDimConst('Measure', measureType),
                HDimConst('Unit', unit)
            ]
        
        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        df = tidy_sheet.topandas()
        sheets.append(df)
        print(tab.name)

df = pd.concat(sheets).fillna('')

# +
df['Marker'] = df.apply(
    lambda x: 'note 5' if '[note 5]' in x['National Communication Sector'] else 'note 4, 5' if '[note 4, 5]' in x['National Communication Sector'] 
    else 'note 6' if '[note 6]' in  x['National Communication Sector'] else 'note 8' if '[note 8]' in x['National Communication Sector'] 
    else '', axis=1)

df['National Communication Sector'] = df.apply(
    lambda x: str(x['National Communication Sector']).rstrip('[note ') if '[note' in x['National Communication Sector'] 
    else x['National Communication Sector'], axis=1)

df['Period'] = df.apply(lambda x: 'year/' + str(x['Period'])[:4] if 'Q' not in x['Period']
                        else 'quarter/' + str(x['Period'])[-4:] + '-' + str(x['Period'])[:2], axis=1)
                        
df = df.replace({'National Communication Sector': {'Agriculture [note 5]': 'Agriculture',
                                                   'Industrial processes [note 5]': 'Industrial processes',
                                                   'Waste management [note 5]': 'Waste management',
                                                   'LULUCF [note 4, 5]': 'LULUCF',
                                                   'Other greenhouse gases [note 6]': 'Other greenhouse gases',
                                                   'Other sectors [note 8]': 'Other sectors'}})

df = df.replace({'National Communication Sector': {'     from power stations': 'Power Stations',
                                                   '     other Energy supply': 'Other Energy Supply',
                                                   'LULUCF': 'land-use-land-use-change-and-forestry'}})

indexNames = df[df['Fuel'] == 'Total'].index
df.drop(indexNames, inplace=True)

df = df.rename(columns={'OBS': 'Value'})
df['Value'] = df['Value'].map(lambda x: round(x, 1))
# -

df = df.drop_duplicates()

for col in df.columns.values.tolist()[2:]:
    try:
        df[col] = df[col].apply(pathify)
    except Exception as err:
        raise Exception('Failed to pathify column "{}".'.format(col)) from err

df = df[['Period', 'Area', 'National Communication Sector',
         'Fuel', 'Marker', 'Measure', 'Unit', 'Value']]

df.to_csv("observations.csv", index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file("catalog-metadata.json")
