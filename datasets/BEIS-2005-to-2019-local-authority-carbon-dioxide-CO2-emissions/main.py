# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
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

df.drop(columns=df.columns.values.tolist()[0:6], axis=1, inplace=True)
df.drop(columns=df.columns.values.tolist()[-2:], axis=1, inplace=True)
df.rename(columns={'Calendar Year': 'Year',
                   'Territorial emissions (kt CO2)': 'Territorial emissions',
                   'Emissions within the scope of influence of LAs (kt CO2)': 'Emissions within the scope of influence of LAs',
                   }, inplace=True)

for col in df.columns.values.tolist()[-2:]:
    df[col] = df[col].astype(str).astype(float).round(2)

df = df.drop_duplicates()
df = df.fillna('unallocated consumption')

df = pd.melt(df, id_vars=['Local Authority Code', 'Year', 'LA CO2 Sector', 'LA CO2 Sub-sector'], value_vars=[
             "Territorial emissions", "Emissions within the scope of influence of LAs"], var_name='Measure', value_name='Value')

df = df[['Year', 'Local Authority Code', 'LA CO2 Sector',
         'LA CO2 Sub-sector', 'Measure', 'Value']]

for col in df.columns.values.tolist()[2:-1]:
    try:
        df[col] = df[col].apply(pathify)
    except Exception as err:
        raise Exception('Failed to pathify column "{}".'.format(col)) from err

df.to_csv('observations.csv', index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')
