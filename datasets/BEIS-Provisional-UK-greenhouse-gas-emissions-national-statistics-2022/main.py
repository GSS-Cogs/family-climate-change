#!/usr/bin/env python
# coding: utf-8
# ## BEIS-Provisional-UK-greenhouse-gas-emissions-national-statistics-2022

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
    # tables 3 and 4 are moving averages
    if tab.name in ['Table1', 'Table2', 'Table5', 'Table6']:
        if tab.name == 'Table2':
            sector = tab.filter('Sector').fill(DOWN).is_not_blank()
            fuel = tab.filter('Fuel Type').fill(DOWN).is_not_blank()
            period = tab.filter('Fuel Type').fill(RIGHT).is_not_blank()
            measureType = 'Carbon-dioxide Emissions'
        else:
            ncSector = tab.filter("NC Sector").fill(DOWN).is_not_blank()
            fuel = 'Total Fuel'
            period = tab.filter("NC Sector").fill(RIGHT).is_not_blank()

        if tab.name in ['Table1', 'Table5']:
            measureType = 'Greenhouse Gas Emissions'
        elif tab.name == 'Table6':
            measureType = 'Temperature-adjusted Greenhouse Gas Emissions'

        area = 'K02000001'
        observations = period.fill(DOWN).is_not_blank()

        if tab.name not in ['Table2']:
            dimensions = [
                HDim(period, "Period", CLOSEST, LEFT),
                HDim(ncSector, "National Communication Sector", DIRECTLY, LEFT),
                HDimConst('Area', area),
                HDimConst('Fuel', fuel),
                HDimConst('Measure', measureType)
            ]
        else:
            dimensions = [
                HDim(period, "Period",  CLOSEST, LEFT),
                HDim(fuel, 'Fuel', DIRECTLY, LEFT),
                HDim(sector, "National Communication Sector", CLOSEST, ABOVE),
                HDimConst('Area', area),
                HDimConst('Measure', measureType),
            ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        df = tidy_sheet.topandas()
        sheets.append(df)
        print(tab.name)

df = pd.concat(sheets).fillna('')

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
                                                   'Other sectors [note 8]': 'Other sectors',
                                                   'Total greenhouse gas emissions': 'Total greenhouse gases'}})

df = df.replace({'National Communication Sector': {'     from power stations': 'Power Stations',
                                                   '     other Energy supply': 'Other Energy Supply',
                                                   'LULUCF': 'land-use-land-use-change-and-forestry'}})

indexNames = df[df['Fuel'] == 'Total'].index
df.drop(indexNames, inplace=True)

df = df.rename(columns={'OBS': 'Value'})
df['Value'] = df['Value'].map(lambda x: round(x, 5))

df['Gas'] = 'CO2'
df['Gas'] = df.apply(lambda x: 'CO2' if x['National Communication Sector'] == 'Total CO2'
                     else 'other-greenhouse-gases' if x['National Communication Sector'] == 'Other greenhouse gases'
                     else 'total-greenhouse-gases' if x['National Communication Sector'] == 'Total greenhouse gases'
                     else x['Gas'], axis=1
                     )

df['National Communication Sector'] = df.apply(lambda x: 'Grand Total' if x['National Communication Sector'] == 'Total CO2'
                                               else 'Grand Total' if x['National Communication Sector'] == 'Other greenhouse gases'
                                               else 'Grand Total' if x['National Communication Sector'] == 'Total greenhouse gases'
                                               else x['National Communication Sector'], axis=1
                                               )

df = df[['Period', 'Area', 'National Communication Sector',
         'Fuel', 'Gas', 'Measure', 'Value']]

for col in ['National Communication Sector', 'Fuel']:
    try:
        df[col] = df[col].apply(pathify)
    except Exception as err:
        raise Exception(
            'Failed to pathify column "{}".'.format(col)) from err

df.to_csv("observations.csv", index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file("catalog-metadata.json")