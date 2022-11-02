import pandas as pd 
from gssutils import *
from csvcubed.models.cube.qb.catalog import CatalogMetadata

df = pd.read_csv("regional-average-climate-observations-uk-annual-rainfall.csv")

df.to_csv('observations.csv', index=False)
catalog_metadata = CatalogMetadata(
    title = "Regional annual average rainfall with trends 1836 - 2021",
    creator_uri = "https://www.gov.uk/government/organisations/the-meteorological-office",
    publisher_uri = "https://www.gov.uk/government/organisations/met-office"
)
catalog_metadata.to_json_file('catalog-metadata.json')
