#!/usr/bin/env python
# coding: utf-8
#     DEFRA-Carbon-Footprint-Summary-Source-Region-90-19

import pandas as pd
from gssutils import *

metadata = Scraper(seed='info.json')

distribution = metadata.distribution(
    mediaType="application/vnd.oasis.opendocument.spreadsheet",
    title=lambda x: "UK full dataset 1990 - 2019, including conversion factors by SIC code"
    in x,
)

metadata.dataset.title = "Carbon Footprint - Summary Source Region 90-19"
metadata.dataset.comment = "CO2: Produced goods, imported goods, generated by households" 

tabs = {tab.name: tab for tab in distribution.as_databaker()}

# +
tidied_sheets = []
for name, tab in tabs.items():
    
    if 'Summary_source_region_90-19' not in name:
        continue

    unwanted_cell = tab.excel_ref("A34").expand(DOWN).expand(RIGHT).is_not_blank()
    period = tab.excel_ref("B4").expand(DOWN).is_not_blank().is_not_whitespace() - unwanted_cell
    country = tab.excel_ref("C2").expand(RIGHT).is_not_blank().is_not_whitespace()
    country_code = tab.excel_ref("C3").expand(RIGHT).is_not_blank().is_not_whitespace()
    observations = tab.excel_ref("C4").expand(DOWN).fill(RIGHT).is_not_blank() - unwanted_cell
    measure = 'Greenhouse gas emissions'
    unit = 'kt CO2e'
    
    dimensions = [
        HDim(period,'Period',DIRECTLY,LEFT),
        HDim(country,'Country',DIRECTLY, ABOVE),
        HDim(country_code, 'Country Code',DIRECTLY,ABOVE),
        HDimConst("Measure", measure),
        HDimConst("Unit", unit)
    ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations) 
    tidied_sheets.append(tidy_sheet.topandas())

# from Carbon Dioxide Emission
    period = tab.excel_ref("B38").expand(DOWN).is_not_blank().is_not_whitespace()
    country = tab.excel_ref("C36").expand(RIGHT).is_not_blank().is_not_whitespace()
    country_code = tab.excel_ref("C37").expand(RIGHT).is_not_blank().is_not_whitespace()
    observations = tab.excel_ref("C38").expand(DOWN).fill(RIGHT).is_not_blank()
    measure = 'Carbon dioxide emissions'
    unit = 'kt CO2'

    dimensions = [
        HDim(period,'Period',DIRECTLY,LEFT),
        HDim(country,'Country',DIRECTLY,ABOVE),
        HDim(country_code, 'Country Code',DIRECTLY,ABOVE),
        HDimConst("Measure", measure),
        HDimConst("Unit", unit)
    ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations) 
    tidied_sheets.append(tidy_sheet.topandas())
    # savepreviewhtml(tidy_sheet,fname=tab.name + "Preview.html")
# -
df = pd.concat(tidied_sheets, sort=True)

df.rename(columns={'OBS' : 'Value'}, inplace=True)
df['Period'] = df['Period'].astype(float).astype(int)
df['Period'] = df['Period'].map(lambda x: 'year/' + str(x))
df['Value'] = df['Value'].astype(float).round(3)
df = df.drop_duplicates()

indexNames = df[df['Country'] == 'Total'].index
df.drop(indexNames, inplace=True)

indexNames = df[df['Country Code'] == 'Total'].index
df.drop(indexNames, inplace=True)

df['Measure'] = df['Measure'].apply(pathify)
df['Unit'] = df['Unit'].apply(pathify)
df = df[['Period', 'Country', 'Country Code', 'Measure', 'Unit', 'Value']]

df.to_csv('observations.csv', index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')