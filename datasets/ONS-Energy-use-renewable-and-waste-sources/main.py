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
# -

tabs = distribution.as_databaker()
tidied_sheets = []
for tab in tabs:
    if 'Contents' in tab.name:
        continue
    remove = tab.excel_ref('A77').expand(DOWN).expand(RIGHT)
    year = tab.excel_ref('B4').expand(RIGHT).is_not_blank()
    observations = year.fill(DOWN).is_not_blank() - remove
    energy_use_type =  tab.excel_ref('A4').expand(DOWN).is_not_blank()
    enery_type = tab.excel_ref('A4').expand(DOWN).is_bold()
    dimensions = [
        HDim(year, 'Year', DIRECTLY, ABOVE),
        HDim(energy_use_type, "Energy use from renewable and waste sources", DIRECTLY, LEFT),
        HDim(enery_type, "Energy Topic", CLOSEST, ABOVE),
    ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    #savepreviewhtml(tidy_sheet, fname = tab.name+ "Preview.html")
    df = tidy_sheet.topandas()
    tidied_sheets.append(df)

df = pd.concat(tidied_sheets, sort=True)
df.rename(columns={'OBS' : 'Value'}, inplace=True)
df['Year'] = df['Year'].astype(str).replace('\.0', '', regex=True)

# +
df['Energy use from renewable and waste sources'] = df['Energy use from renewable and waste sources'].apply(pathify)

df['Energy Topic'] = df['Energy Topic'].apply(pathify)
f1=((df['Energy Topic'] == df['Energy use from renewable and waste sources']))
df.loc[f1,'Energy Topic'] = 'total'

df = df[['Year', 'Energy use from renewable and waste sources', 'Energy Topic', 'Value']]
cubes.add_cube(metadata, df.drop_duplicates(), title)
cubes.output_all()
