#!/usr/bin/env python
# coding: utf-8
# ## Energy Intensity Extract 1970-2021

#
import pandas as pd
from gssutils import *
import numpy as np

metadata = Scraper(seed='info.json')
metadata.dataset.family = 'climate-change'
metadata.dataset.title = 'Energy Intensity Extract 1970 - 2021'
metadata.dataset.contactPoint = "energy.stats@beis.gov.uk"

distribution = metadata.distribution(mediaType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                     title=lambda x: "ECUK 2022: Energy intensity data tables (Excel)"
                                     in x,
                                     )

tabs = {tab.name: tab for tab in distribution.as_databaker()}
# +
tidied_sheets = []

# from table I2
tab = tabs['Table I2']
unwanted_cells = tab.excel_ref("A59").expand(RIGHT).expand(DOWN)
unwanted_measure = tab.excel_ref("E7").expand(
    RIGHT)
unwanted_obs = tab.excel_ref("E8").expand(
    RIGHT).expand(DOWN)
year = tab.excel_ref("A8").expand(
    DOWN).is_not_blank() - unwanted_cells
measure_type = tab.excel_ref("B7").expand(
    RIGHT).is_not_blank() - unwanted_measure
sector = "Road"
observations = tab.excel_ref("B8").expand(DOWN).expand(
    RIGHT).is_not_blank() - unwanted_obs - unwanted_cells

dimensions = [
    HDim(year, 'Year', CLOSEST, ABOVE),
    HDim(measure_type, 'Measure Type', DIRECTLY, ABOVE),
    HDimConst("Sector", sector)
]

tidy_sheet = ConversionSegment(tab, dimensions, observations)
df = tidy_sheet.topandas()
df.replace({'Measure Type': {'Consumption (ktoe)': 'Road Passenger Consumption (ktoe)',
                             'Energy consumption per billion passenger kilometres (ktoe)': 'Energy consumption per unit of output (ktoe)'}}, inplace=True)
tidied_sheets.append(df)

# from table I3
tab = tabs["Table I3"]
unwanted_cells = tab.excel_ref("A58").expand(RIGHT).expand(DOWN)
unwanted_obs = tab.excel_ref("E6").expand(
    RIGHT).expand(DOWN)
unwanted_measure = tab.excel_ref("E5").expand(
    RIGHT)
year = tab.excel_ref("A6").expand(
    DOWN).is_not_blank() - unwanted_cells
measure_type = tab.excel_ref("B5").expand(
    RIGHT).is_not_blank() - unwanted_measure
sector = "Household"
observations = tab.excel_ref("B6").expand(DOWN).expand(
    RIGHT).is_not_blank() - unwanted_obs - unwanted_cells

dimensions = [
    HDim(year, 'Year', CLOSEST, ABOVE),
    HDim(measure_type, 'Measure Type', DIRECTLY, ABOVE),
    HDimConst("Sector", sector)
]

tidy_sheet = ConversionSegment(tab, dimensions, observations)
df = tidy_sheet.topandas()
df.replace({"Measure Type": {'Total Final Consumption (ktoe)': 'Total Final Domestic Consumption (ktoe)'
                             }}, inplace=True)
tidied_sheets.append(df)

# from table I4
tab = tabs['Table I4']
unwanted_cells = tab.excel_ref("A60").expand(RIGHT).expand(DOWN)
unwanted_obs = tab.excel_ref("CG8").expand(
    RIGHT).expand(DOWN)
unwanted_measure = tab.excel_ref("CG7").expand(
    RIGHT)
year = tab.excel_ref("CC8").expand(
    DOWN).is_not_blank() - unwanted_cells
measure_type = tab.excel_ref("CD7").expand(
    RIGHT).is_not_blank() - unwanted_measure
sector = "Industrial"
observations = tab.excel_ref("CD8").expand(DOWN).expand(
    RIGHT).is_not_blank() - unwanted_obs - unwanted_cells

dimensions = [
    HDim(year, 'Year', CLOSEST, ABOVE),
    HDim(measure_type, 'Measure Type', DIRECTLY, ABOVE),
    HDimConst("Sector", sector)
]

tidy_sheet = ConversionSegment(tab, dimensions, observations)
df = tidy_sheet.topandas()
df.replace({"Measure Type": {'Consumption (ktoe)': 'Industrial Consumption (ktoe)',
                             'Output': 'Industrial Output'
                             }}, inplace=True)
tidied_sheets.append(df)

# from table I5
tab = tabs['Table I5']
unwanted_cells = tab.excel_ref("Q60").expand(
    RIGHT).expand(DOWN)
unwanted_obs = tab.excel_ref("U8").expand(
    RIGHT).expand(DOWN)
unwanted_measure = tab.excel_ref("U7").expand(
    RIGHT)

year = tab.excel_ref("Q8").expand(DOWN).is_not_blank() - unwanted_cells
measure_type = tab.excel_ref("R7").expand(
    RIGHT).is_not_blank() - unwanted_measure
sector = "Services"
observations = tab.excel_ref("R8").expand(DOWN).expand(
    RIGHT).is_not_blank() - unwanted_obs - unwanted_cells

dimensions = [
    HDim(year, 'Year', CLOSEST, ABOVE),
    HDim(measure_type, 'Measure Type', DIRECTLY, ABOVE),
    HDimConst("Sector", sector)
]

tidy_sheet = ConversionSegment(tab, dimensions, observations)
df = tidy_sheet.topandas()
df.replace({"Measure Type": {'Consumption (ktoe)': 'Service Consumption Excluding Agriculture (ktoe)',
                             'Output': 'Service Output',
                             'Consumption per unit of output (ktoe)': 'Energy Consumption per unit of output 1 (ktoe)'
                             }}, inplace=True)
tidied_sheets.append(df)
# -

df = pd.concat(tidied_sheets, sort=True, axis=0).fillna('')

df = df.rename(columns={'OBS': 'Value'})
df.replace({"Year": {'2008 3': '2008'}}, inplace=True)
df['Year'] = df['Year'].astype(float).astype(int)

df["Unit"] = df['Measure Type'].str.extract('.*\((.*)\).*')
df['Measure Type'] = df['Measure Type'].str.replace(r"\(.*\)", "").str.strip()
df.replace(
    {'Measure Type': {'No Households': "Number of Households 000s"}}, inplace=True)
df.replace({'Unit': {"'000s": "count", }}, inplace=True)
df["Unit"].fillna("unknown", inplace=True)
df['Unit'] = df['Unit'].str.capitalize()

df['Sector'] = df['Sector'].apply(pathify)

df = df.replace(r'^\s*$', np.nan, regex=True)
df = df.dropna(subset=['Value'])

df['Value'] = pd.to_numeric(df['Value'], errors="raise", downcast="float")
df["Value"] = df["Value"].astype(float).round(3)

df = df[['Year', 'Measure Type', 'Sector', 'Unit', 'Value']]

df.to_csv('observations.csv', index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')