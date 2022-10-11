#%%
import json 
import pandas as pd 
from gssutils import *
from csvcubed.models.cube.qb.catalog import CatalogMetadata # need this extra import when working with local CSV files


df = pd.read_csv("raw.csv")
#%%

df.rename(columns={
                "Year": "Period",
                "England": "Value"
                }, inplace=True)

#create out directory for all output files
df.to_csv('observations.csv', index=False) #defra_e8_efficient_use_of_water_20_21-
catalog_metadata = CatalogMetadata(
    title = "E8: Efficient use of water 20 - 21",
    description = "Per capita water consumption (Litres/person/day)."
)
catalog_metadata.to_json_file('catalog-metadata.json')