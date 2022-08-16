# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.8
#   kernelspec:
#     display_name: Python 3.9.1 64-bit
#     language: python
#     name: python3
# ---

# ## BEIS-2005-to-2019-local-authority-carbon-dioxide-CO2-emissions

import json
import pandas as pd
from gssutils import *

metadata = Scraper(seed='info.json')
distribution = metadata.distribution(latest=True, mediaType='text/csv',
                                     title=lambda x: 'local authority carbon dioxide (CO2) emissions dataset' in x)

metadata.dataset.title = distribution.title
df = distribution.as_pandas()

df.drop(columns=df.columns.values.tolist()[1:5], axis=1, inplace=True)
df.rename(columns={'Calendar Year': 'Year',
                   'Territorial emissions (kt CO2)': 'Territorial emissions',
                   'Emissions within the scope of influence of LAs (kt CO2)': 'Emissions within the scope of influence of LAs',
                   'Mid-year Population (thousands)': 'Population',
                   'Area (km2)': 'Area'
                   }, inplace=True)

df['Territorial Emissions per capital'] = df['Territorial emissions']/df['Population']
df['Territorial Emissions per area'] = df['Territorial emissions']/df['Area']

for col in ['Territorial emissions', 'Emissions within the scope of influence of LAs',
            'Territorial Emissions per capital', 'Territorial Emissions per area']:
    df[col] = df[col].astype(str).astype(float).round(2)

df = pd.melt(df, id_vars=['Country', 'Local Authority', 'Local Authority Code', 'Year', 'LA CO2 Sector', 'LA CO2 Sub-sector'], value_vars=[
             "Territorial emissions", "Emissions within the scope of influence of LAs", 'Territorial Emissions per capital', 'Territorial Emissions per area'], var_name='Measure', value_name='Value')

df['Unit'] = df.apply(lambda x: 'kt CO2' if x['Measure'] == 'Territorial emissions' else 'kt CO2' if x['Measure'] == 'Emissions within the scope of influence of LAs' else 'CO2/person' if x['Measure']
                      == 'Territorial Emissions per capital' else 'CO2/m2' if x['Measure'] == 'Territorial Emissions per area' else ' ', axis=1)

df = df.drop_duplicates()
df = df.fillna('Unallocated consumption')

df = df[['Year', 'Country', 'Local Authority', 'Local Authority Code', 'LA CO2 Sector',
         'LA CO2 Sub-sector', 'Measure', 'Value', 'Unit']]

df.to_csv('observations.csv', index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')