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
from gssutils import Cubes, Scraper, pathify

cubes = Cubes('info.json')
info = json.load(open('info.json'))
landingPage = info['landingPage']
metadata = Scraper(seed='info.json')
distribution = metadata.distribution(mediaType='text/csv')
metadata.dataset.title = distribution.title

df = distribution.as_pandas()

df = (
    distribution
    .as_pandas()
    .assign(**{"Local Authority Code": lambda df: df["Local Authority Code"].combine_first(df["Local Authority"])})
    .drop(columns=df.columns[0:6])
    .drop(columns=['Mid-year Population (thousands)', 'Area (km2)'])
    .rename(columns={
        'Calendar Year': 'Year',
        'Territorial emissions (kt CO2)':'Territorial emissions',
        'Emissions within the scope of influence of LAs (kt CO2)': 'Emissions within the scope of influence of LAs'
    })
)

val_vars = ['Territorial emissions', 'Emissions within the scope of influence of LAs']
other_vars = df.columns.difference(val_vars)
df = pd.melt(
    df, 
    id_vars=other_vars, 
    value_vars=val_vars, 
    var_name='Measure Type',
    value_name='Value'
)

df["Local Authority Code"] = (
    df["Local Authority Code"]
    .replace({
        "Unallocated consumption": pathify("Unallocated consumption"),
        "Large elec users (high voltage lines) unknown location": pathify("Large elec users (high voltage lines) unknown location")
    })
    .map(lambda x: (
        f"http://gss-data.org.uk/data/gss_data/climate-change/beis-2005-to-2019-local-authority-carbon-dioxide-co2-emissions#concept/local-authority-code/{x}" if x in [
            pathify("Unallocated consumption"), 
            pathify("Large elec users (high voltage lines) unknown location")
        ] else f"http://statistics.data.gov.uk/id/statistical-geography/{x}"
    ))
)

for col in df.columns.values.tolist()[-1:]:
    df[col] = df[col].astype(str).astype(float).round(2)
for col in ['LA CO2 Sector', 'LA CO2 Sub-sector', 'Measure Type']:
    try:
        df[col] = df[col].apply(pathify)
    except Exception as err:
        raise Exception('Failed to pathify column "{}".'.format(col)) from err

df['Units'] = 'kt-co2'

cubes.add_cube(metadata, df, metadata.dataset.title)
cubes.output_all()
