# %%
import pandas as pandas
from gssutils import *
import pandas as pd
from csvcubed.models.cube.qb.catalog import CatalogMetadata


df = pd.read_excel("Ch1_Woodland_FS2022.xlsx",
                   sheet_name='Fig_1.1_data', skiprows=4)
df = pd.melt(frame=df, id_vars=['Year'],
             var_name='Country', value_name='Value')
df['Country'] = df['Country'].str.split(" \n").str[0]
df = df.replace({'Country': {"UK": "E92000001", "Northern Ireland": "N92000002",
                             "Scotland": "S92000003", "Wales": "W92000004", "England": "E92000001"}})

df.to_csv("observations.csv", index=False)
catalog_metadata = CatalogMetadata(
    title = "Forestry Statistics 2022 Woodland Area"
)

catalog_metadata.to_json_file('catalog-metadata.json')
# %%
