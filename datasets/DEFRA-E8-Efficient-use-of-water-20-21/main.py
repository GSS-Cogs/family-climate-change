#              DEFRA-E8-EFFICIENT-USE-OF-WATER-20-21"

import pandas as pd 
from gssutils import *
from csvcubed.models.cube.qb.catalog import CatalogMetadata

df = pd.read_csv("raw.csv")
df['Year'] = df['Year'].str.replace(r'-20', r'-')
df = pd.melt(df, id_vars=['Year'])
df.rename(columns={'variable': 'Geography','value': 'Value'}, inplace=True)

df.to_csv('observations.csv', index=False) 
catalog_metadata = CatalogMetadata(
    title = "E8: Efficient use of water 20 - 21",
    summary = "",
    description = "Summary of geographical water consumption in England Only."
)
catalog_metadata.to_json_file('catalog-metadata.json')
