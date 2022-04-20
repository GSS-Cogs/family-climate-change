import pandas as pd 
from gssutils import *
from csvcubed.models.cube.qb.catalog import CatalogMetadata
from datetime import datetime

df = pd.read_csv("raw.csv")
df = pd.melt(df, id_vars=['period-start'])
df.rename(columns={'period-start': 'Year','variable': 'Geography','value': 'Value'}, inplace=True)
df['Geography'] = df['Geography'].apply(pathify)

df.to_csv('observations.csv', index=False)
catalog_metadata = CatalogMetadata(
    title = "regional average climate observations UK Annual rain days 95 percentile",
    description = "Priority dataset for Climate Change Platform project."
)
catalog_metadata.to_json_file('catalog-metadata.json')
