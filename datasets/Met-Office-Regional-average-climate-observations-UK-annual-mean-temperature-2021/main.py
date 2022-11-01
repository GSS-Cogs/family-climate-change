import pandas as pd 
from gssutils import *
from csvcubed.models.cube.qb.catalog import CatalogMetadata
from datetime import datetime

df = pd.read_csv("raw.csv")

df['Year'] = df['Year'].astype(str).astype(int)

df.to_csv('observations.csv', index=False)
catalog_metadata = CatalogMetadata(
    title = "regional average climate observations uk annual mean temperature 21",
    creator_uri = "https://www.gov.uk/government/organisations/the-meteorological-office",
    publisher_uri = "https://www.gov.uk/government/organisations/met-office",
    description = "Priority dataset for Climate Change Platform project."
)
catalog_metadata.to_json_file('catalog-metadata.json')
