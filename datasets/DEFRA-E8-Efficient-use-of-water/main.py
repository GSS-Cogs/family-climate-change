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

# + [markdown] tags=[]
# ## DEFRA-E8-Efficient-use-of-water
# -

import json
import pandas as pd
from gssutils import *

cubes = Cubes('info.json')
info = json.load(open('info.json'))
landingPage = info['landingPage']
landingPage

metadata = Scraper(seed='info.json')

metadata.select_dataset(title = lambda x: 'E8' in x)

distribution = metadata.distribution(mediaType="text/csv")
metadata.dataset.title = distribution.title
metadata.dataset.family = 'DEFRA'

df = distribution.as_pandas()

df['Year'] = df['Year'].str.replace(r'-', r'-20')

df['Value'] = pd.to_numeric(df['Value'], downcast='float')
df['Value'] = df['Value'].astype(str).astype(float).round(2)
df = df.fillna('')

df['Series'] = df['Series'].apply(pathify)

cubes.add_cube(metadata, df.drop_duplicates(), metadata.dataset.title)
cubes.output_all()
