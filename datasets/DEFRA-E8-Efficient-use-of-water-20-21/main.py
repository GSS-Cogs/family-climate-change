# DEFRA-E8-EFFICIENT-USE-OF-WATER-20-21"

import pandas as pd 
from gssutils import *
from csvcubed.models.cube.qb.catalog import CatalogMetadata

df = pd.read_csv("raw.csv")
df['Year'] = df['Year'].str.replace(r'-20', r'-')
df['Year'] = df.apply(lambda x: 'government-year/' + x['Year'], axis = 1)
df = df.rename(columns={'Year' : 'Period'})
df = pd.melt(df, id_vars=['Period'])
df.rename(columns={'variable': 'Geography','value': 'Value'}, inplace=True)
df = df.drop('Geography', axis = 1)
df.drop_duplicates()

df.to_csv('observations.csv', index=False) 
catalog_metadata = CatalogMetadata(
    title = "E8: Efficient use of water 20 - 21",
    summary = "Part of The Outcome Indicator Framework, a comprehensive set of indicators describing environmental change that relates to the 10 goals within the 25 Year Environment Plan. The framework contains 66 indicators, arranged into 10 broad themes. The indicators are extensive; they cover natural capital assets (for example, land, freshwater, air and seas) and together they show the condition of these assets, the pressures acting upon them and the provision of services or benefits they provide.",
)
catalog_metadata.to_json_file('catalog-metadata.json')
