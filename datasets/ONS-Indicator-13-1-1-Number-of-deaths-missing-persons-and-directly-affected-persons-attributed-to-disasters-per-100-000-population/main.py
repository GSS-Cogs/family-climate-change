# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.4
#   kernelspec:
#     display_name: Python 3.8.8 64-bit
#     name: python3
# ---

# # Number of deaths attributed to disasters per 100,000 population

import json
import pandas as pd
from gssutils import *

cubes = Cubes('info.json')

info = json.load(open('info.json'))
dataURL = info['dataURL']
dataURL

#

metadata = Scraper(seed='info.json')
metadata

distribution = metadata.distribution(mediaType='text/csv')
distribution

title = "Indicator 13.1.1: Number of deaths, missing persons and directly affected persons attributed to disasters per 100,000 population"
metadata.dataset.title = title

df = distribution.as_pandas().fillna('')


#

df.loc[(df['Units'] == 'Rate per 100,000 population'), 'Value'] = df['Value'].round(2)
df = df.replace('', 'not-available')

for col in df.columns.values.tolist()[1:-2]:
	df[col] = df[col].apply(pathify)

cubes.add_cube(metadata, df, metadata.dataset.title)
cubes.output_all()
