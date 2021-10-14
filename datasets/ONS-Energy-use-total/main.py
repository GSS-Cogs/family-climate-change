# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.5
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# +
import json
import pandas as pandas
from gssutils import *

cubes = Cubes('info.json')
info = json.load(open('info.json'))
landingPage = info['landingPage']
metadata = Scraper(seed="info.json")
distribution = metadata.distribution(latest = True, mediaType = Excel)
title = distribution.title
distribution
# -

tabs = distribution.as_databaker()
tidied_sheets = []
for tab in tabs:
    if 'Contents' in tab.name:
        continue
    year = tab.excel_ref('B4').expand(RIGHT).is_not_blank()
    observations = year.fill(DOWN).is_not_blank()
    source = tab.excel_ref('A4').expand(DOWN).is_bold()
    industry_section = tab.excel_ref('A4').expand(DOWN).is_not_blank()
    unit = tab.excel_ref('AD3')
    
    dimensions = [
        HDim(year, 'Year', DIRECTLY, ABOVE),
        HDim(source, "Energy Consumption Source", CLOSEST, ABOVE),
        HDim(industry_section, "Industry Section", DIRECTLY, LEFT),
        HDim(unit, 'Unit', CLOSEST, ABOVE),
    ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    #savepreviewhtml(tidy_sheet, fname = tab.name+ "Preview.html")
    df = tidy_sheet.topandas()
    tidied_sheets.append(df)


df = pd.concat(tidied_sheets, sort=True)
df.rename(columns={'OBS' : 'Value'}, inplace=True)
df['Year'] = df['Year'].astype(str).replace('\.0', '', regex=True)

df['Industry Section'] = df['Industry Section'].apply(pathify)
df['Energy Consumption Source'] = df['Energy Consumption Source'].apply(pathify)
df['Measure Type'] = 'gross-caloric-values'
df["Unit"]= df['Unit'].str.extract('.*\((.*)\).*')
df['Unit'] = df['Unit'].apply(pathify)
df = df[['Year', 'Energy Consumption Source', 'Industry Section', 'Value', 'Measure Type', 'Unit']]
cubes.add_cube(metadata, df.drop_duplicates(), title)
cubes.output_all()
df
