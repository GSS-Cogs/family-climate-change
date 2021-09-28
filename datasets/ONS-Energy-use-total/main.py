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
    if "(Mtoe)" in tab.name: 
        unit = 'Millions of tonnes of oil equivalent (Mtoe)'
    if "(PJ)" in tab.name: 
        unit = 'Energy Consumption in Petajoules (PJ)'
    
    dimensions = [
        HDim(year, 'Year', DIRECTLY, ABOVE),
        HDim(source, "Source", CLOSEST, ABOVE),
        HDim(industry_section, "Industry Section", DIRECTLY, LEFT),
        HDimConst('Unit', unit),
    ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    #savepreviewhtml(tidy_sheet, fname = tab.name+ "Preview.html")
    df = tidy_sheet.topandas()
    tidied_sheets.append(df)
    

df = pd.concat(tidied_sheets, sort=True)
df.rename(columns={'OBS' : 'Value'}, inplace=True)
df['Year'] = df['Year'].astype(str).replace('\.0', '', regex=True)

# Notes 
# - Source values have been taken from the bold values held within cells a4 down: 
#        'Total energy consumption of primary fuels and equivalents',
#        'Direct1 use of energy from fossil fuels',
#        'Energy from other sources',
#        'Direct use of energy including other sources',
#        'Reallocated1 use of energy'
#        
# - Industry section values have been taken from all cells from a4 down including those used inside the Source diemension aswell. I am not sure if this is ok / they need to be reworded as a 'total' situation. 
#
# - each tab has a different unit which I have populated the unit dimension with. 

df['Industry Section'] = df['Industry Section'].apply(pathify)
df['Source'] = df['Source'].apply(pathify)
df = df[['Year', 'Source', 'Industry Section', 'Value', 'Unit']]
cubes.add_cube(metadata, df.drop_duplicates(), title)
cubes.output_all()
df
