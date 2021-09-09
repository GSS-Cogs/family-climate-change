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

# ## DEFRA-B3-State-of-the-water-environment

import json
import pandas as pandas
from gssutils import *

cubes = Cubes('info.json')
info = json.load(open('info.json'))
landingPage = info['landingPage']
landingPage

metadata = Scraper(seed="info.json")
metadata.select_dataset(title = lambda x: "B3" in x) 

distribution = metadata.distribution(mediaType="text/csv")
metadata.dataset.title = distribution.title
metadata.dataset.family = 'DEFRA'

df = distribution.as_pandas().fillna('')

df['Label'] = df['Year'].str.extract(r'([^(\d+)]+)')
df['Year'] = df['Year'].str.extract(r'(\d+)')

# + tags=[]
df = df[['Year', 'Label', 'Series', 'Component', 'Status category', 'Value']]
# -

for col in df.columns.to_list()[1:-1]:
    try:
        df[col] = df[col].apply(pathify)
    except Exception as err:
        raise Exception('Failed to pathify column "{}".'.format(col)) from err

# + tags=[]
cubes.add_cube(metadata, df, metadata.dataset.title)
cubes.output_all()
