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

# ONS-Energy-use-renewable-and-waste-sources

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
    energy_use_type =  tab.excel_ref('A4').expand(DOWN).is_not_blank()
    
    dimensions = [
        HDim(year, 'Period', DIRECTLY, ABOVE),
        HDim(energy_use_type, "Energy use from renewable and waste sources", DIRECTLY, LEFT),
    ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    df = tidy_sheet.topandas()
    tidied_sheets.append(df)

df = pd.concat(tidied_sheets, sort=True)
df.rename(columns={'OBS' : 'Value'}, inplace=True)
df['Period'] = df['Period'].astype(str).replace('\.0', '', regex=True)

df['Energy use from renewable and waste sources'] = df['Energy use from renewable and waste sources'].apply(pathify)
df = df[['Period', 'Energy use from renewable and waste sources', 'Value']]
cubes.add_cube(metadata, df.drop_duplicates(), title)
cubes.output_all()
df
