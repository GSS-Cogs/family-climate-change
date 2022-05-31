import pandas as pd 
from gssutils import *
from csvcubed.models.cube.qb.catalog import CatalogMetadata
from datetime import datetime

df = pd.read_csv("raw.csv")

df = pd.melt(df, id_vars=['Year'])

df.rename(columns={'value': 'Value',
                   'variable':'Measure Type'}, inplace=True)

df

df["Measure Type"].unique()

df.to_csv('observations.csv', index=False)
catalog_metadata = CatalogMetadata(
    title = "Energy Efficiency Ratings New Homes",
    description = "Summary of energy efficiency rating by new homes"
)
catalog_metadata.to_json_file('catalog-metadata.json')
