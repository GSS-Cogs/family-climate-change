# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.10.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# + tags=[]
import json
import pandas as pd
from gssutils import *
# -

cubes = Cubes('info.json')

info = json.load(open('info.json'))
landingPage = info['landingPage']

metadata = Scraper(seed='info.json')

distribution = metadata.distributions[-1]

title = distribution.title
metadata.dataset.title = title

df = distribution.as_pandas(encoding='ISO-8859-1').fillna(' ')

df.drop(df.columns[df.columns.str.contains('Unnamed',case = False)],axis = 1, inplace = True)
df.drop('National Communication Sub-sector', axis=1, inplace=True)

df.rename(columns={'TerritoryName' : 'Geography Code', 'EmissionUnits' : 'Emission Units'}, inplace=True)

df['Emission'] = df['Emission'].astype(float).round(5)

for col in df.columns.values.tolist():
    if col in ['GHG', 'GHG Grouped', 'IPCC Code', 'Emission Units', 'National Communication Sub-sector', 'Year', 'Emission']: 
        continue
    try:
        df[col] = df[col].apply(pathify)
    except Exception as err:
        raise Exception('Failed to pathify column "{}".'.format(col)) from err

cubes.add_cube(metadata, df, metadata.dataset.title)
cubes.output_all()
