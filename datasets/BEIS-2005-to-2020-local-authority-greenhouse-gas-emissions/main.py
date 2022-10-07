import json
import pandas as pd
import numpy as np
from gssutils import *

metadata = Scraper(seed='info.json')

distribution = metadata.distribution(latest = True, mediaType = "text/csv",
                                        title = lambda x: "2005 to 2020 local authority greenhouse gas emissions dataset" in x)

df = distribution.as_pandas()

df.rename(columns={"Calendar Year": "Year",
                    "Greenhouse gas": "Greenhouse Gas",
                    "Territorial emissions (kt CO2e)": "Territorial emissions",
                    "CO2 emissions within the scope of influence of LAs (kt CO2e)": "Emissions within the scope of influence of LAs",
                    "Mid-year Population (thousands)": "Population",
                    "Area (km2)": "Area"}, inplace = True)

df["Territorial emissions per capita"] = df["Territorial emissions"]/df["Population"]
df["Territorial emissions per area"] = df["Territorial emissions"]/df["Area"]

for col in ['Territorial emissions', 'Emissions within the scope of influence of LAs',
            'Territorial emissions per capita', 'Territorial emissions per area']:
    df[col] = df[col].astype(str).astype(float).round(4)

val_vars=["Territorial emissions", "Emissions within the scope of influence of LAs", 'Territorial emissions per capita', 'Territorial emissions per area']
other_vars = df.columns.difference(val_vars)
df = pd.melt(
    df, 
    id_vars=other_vars, 
    value_vars=val_vars, 
    var_name='Measure',
    value_name='Value'
)


df['Unit'] = df.apply(lambda x: 'kt CO2' if x['Measure'] == 'Territorial emissions' else 'kt CO2' if x['Measure'] == 'Emissions within the scope of influence of LAs' else 'tonnes of CO2' if x['Measure']
                      == 'Territorial emissions per capita' else 'CO2/m2' if x['Measure'] == 'Territorial emissions per area' else ' ', axis=1)

df = df.fillna('unallocated consumption')

df = df[['Year', 'Country', 'Country Code', 'Region', 'Region Code', 
       'Local Authority', 'Local Authority Code', 'LA GHG Sector', 'LA GHG Sub-sector',
       'Greenhouse Gas', 'Second Tier Authority',
       'Measure', 'Value', 'Unit']]

df.to_csv('observations.csv', index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')