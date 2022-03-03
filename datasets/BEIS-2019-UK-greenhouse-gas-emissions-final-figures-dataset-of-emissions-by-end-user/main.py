# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.7
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# ## BEIS-2019-UK-greenhouse-gas-emissions-final-figures-dataset-of-emissions-by-end-user

# + tags=[]
import pandas as pd
from gssutils import *
# -

metadata = Scraper(seed='info.json')

metadata.dataset.family = 'climate-change'

distribution  = metadata.distribution(latest=True, mediaType="text/csv", title = lambda x:"UK greenhouse gas emissions: final figures – dataset of emissions by end user" in x)

df = distribution.as_pandas(encoding='ISO-8859-1').fillna(' ')

df.loc[(df['National Communication Sub-sector'] == ' '), 'National Communication Sub-sector'] = 'Not Applicable'
df.loc[(df['National Communication Category'] == ' '), 'National Communication Category'] = 'Not Applicable'
df.loc[(df['National Communication Fuel'] == ' '), 'National Communication Fuel'] = 'Not Applicable'
df.loc[(df['National Communication Fuel Group'] == ' '), 'National Communication Fuel Group'] = 'Not Applicable'

df.drop(columns=['TerritoryName', 'EmissionUnits'], axis=1, inplace=True)
df.drop(df.columns[df.columns.str.contains('Unnamed',case = False)],axis = 1, inplace = True)
df.query("(not `IPCC Code` == 'Aviation_Bunkers') & (not `IPCC Code` == 'Marine_Bunkers') & (not `IPCC Code` == 'non-IPCC')", inplace = True)

df.rename(columns={'ActivityName' : 'Activity Name','Emission' : 'Value'},inplace=True)

df['Value'] = df['Value'].astype(float).round(3)

# Fix BEIS' use of slashes in some columns:
df['National Communication Category'] = df['National Communication Category'].str.replace('/', '-')
df['Source'] = df['Source'].str.replace('/', '-').str.replace('-+', '-', regex = True)

df.to_csv('observations.csv', index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')
