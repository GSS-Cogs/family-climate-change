import pandas as pd 
from gssutils import *
from csvcubed.models.cube.qb.catalog import CatalogMetadata
from datetime import datetime

df = pd.read_csv("raw.csv", encoding='ISO-8859-1')

df = pd.melt(df, id_vars=['Year'])

df.rename(columns={ 'variable': 'Geography','value': 'Value'}, inplace=True)

df['Geography'] = df['Geography'].apply(pathify)

df['Year'] = df['Year'].astype(str)

df.to_csv('observations.csv', index=False)
catalog_metadata = CatalogMetadata(
    title = "Annual growing season length with trends actual",
    description = "Priority dataset for Climate Change Platform project."
)
catalog_metadata.to_json_file('catalog-metadata.json')
