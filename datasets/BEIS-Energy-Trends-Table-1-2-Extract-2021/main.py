#!/usr/bin/env python
# coding: utf-8
# ### Energy Trends Table 1.2 - Extract 2021

import pandas as pd
from gssutils import *

metadata = Scraper(seed='info.json')

distribution = metadata.distribution(mediaType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                     title=lambda x: "Inland energy consumption: primary fuel input basis (ET 1.2 - monthly)"
                                     in x,
                                     )

tabs = distribution.as_databaker()

tidied_sheets = []
for tab in tabs:

    if tab.name == 'Annual':

        pivot = tab.filter("Year")
        unwanted_cells = tab.excel_ref("J5").expand(RIGHT).is_not_blank()
        year = pivot.fill(DOWN).is_not_blank().is_not_whitespace()
        fuel = pivot.shift(2, 0).expand(
            RIGHT).is_not_blank().is_not_whitespace() - unwanted_cells
        observations = fuel.fill(DOWN).is_not_blank().is_not_whitespace()

        dimensions = [
            HDim(year, 'Year', CLOSEST, ABOVE),
            HDim(fuel, 'Fuel', DIRECTLY, ABOVE),
        ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        # # savepreviewhtml(tidy_sheet, fname= tab.name + "Preview.html")
        tidied_sheets.append(tidy_sheet.topandas())

df = pd.concat(tidied_sheets, sort=True).fillna('')

df = df.rename(columns={'OBS': 'Value'})
df['Year'] = df['Year'].astype(float).astype(int)
df['Value'] = df['Value'].astype(str).astype(float).round(2)

df.replace({'Coal [note 2]': 'Coal',
            'Petroleum [note 3]': 'Petroleum',
            'Natural gas [note 4]': 'Natural gas',
            'Bioenergy & waste [note 5 ] [note 6] [note 7]': 'Bioenergy and waste',
            'Primary electricity - nuclear': 'Nuclear',
            'Primary electricity - wind, solar and hydro [note 8]': 'Wind, solar and hydro',
            'Primary electricity - net imports': 'Net imports'
            }, inplace=True)

df['Fuel'] = df['Fuel'].apply(pathify)
df = df.drop_duplicates()
df = df[['Year', 'Fuel', 'Value']]

metadata.dataset.family = 'climate-change'
metadata.dataset.title = "Inland energy consumption: primary fuel input basis 2021"
metadata.dataset.comment = """
An overview of the trends in energy consumption in the United Kingdom.
"""
metadata.dataset.description = ''' 
An overview of the trends in energy consumption in the United Kingdom for the previous quarter, focusing on: \n\nconsumption, both primary and final by broad sector \ndependency rates of imports, fossil fuels and low carbon fuels \n\nWe publish this document on the last Thursday of each calendar quarter (March, June, September and December)

'''
metadata.dataset.contactPoint = "energy.stats@beis.gov.uk"

df.to_csv('observations.csv', index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')