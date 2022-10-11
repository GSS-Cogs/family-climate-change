#         DEFRA-UK-WATER-LEAKAGE-20-21

import pandas as pd 
from gssutils import *
from csvcubed.models.cube.qb.catalog import CatalogMetadata

df = pd.read_csv("raw.csv")

df['Year'] = df['Year'].str.replace('-20', '-')
df = pd.melt(df, id_vars=['Year'])
df.rename(columns={'variable': 'Geography','value': 'Value'}, inplace=True)

df.to_csv('observations.csv', index=False)
catalog_metadata = CatalogMetadata(
    title = "UK Water Leakage 20 - 21",
    description = "Summary of geographical water leaakage in England Only"
)
catalog_metadata.to_json_file('catalog-metadata.json')