# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.10.2
#   kernelspec:
#     display_name: Python 3.8.8 64-bit
#     name: python3
# ---

# ## BEIS-2005-to-2019-local-authority-carbon-dioxide-CO2-emissions

import json
import pandas as pd
from gssutils import *

cubes = Cubes('info.json')

info = json.load(open('info.json'))
landingPage = info['landingPage']

metadata = Scraper(seed='info.json')

distribution = metadata.distribution(mediaType='text/csv')

metadata.dataset.title = distribution.title

df = distribution.as_pandas()

df.drop(columns=df.columns.values.tolist()[0:6], axis=1, inplace=True)
df.rename(columns={'Calendar Year': 'Year',
					'Territorial emissions (kt CO2)':'Territorial emissions',
					'Emissions within the scope of influence of LAs (kt CO2)': 'Emissions within the scope of influence of LAs',
					'Mid-year Population (thousands)':'Mid-year Population',
					'Area (km2)': 'Area' 
			}, inplace=True)

for col in df.columns.values.tolist()[-4:]:
    if col == 'Mid-year Population':
        df[col] = df[col].astype(str).astype(float).round(3)
    else:
        df[col] = df[col].astype(str).astype(float).round(2)

for col in ['LA CO2 Sector', 'LA CO2 Sub-sector']:
    try:
        df[col] = df[col].apply(pathify)
    except Exception as err:
        raise Exception('Failed to pathify column "{}".'.format(col)) from err

df = df.fillna(' ')

cubes.add_cube(metadata, df, metadata.dataset.title)
cubes.output_all()
