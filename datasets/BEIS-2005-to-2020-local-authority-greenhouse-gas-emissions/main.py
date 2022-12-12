# ### BEIS 2005 to 2020 local authority greenhouse gas emissions
# %%
import json
import pandas as pd
import numpy as np
from gssutils import *

metadata = Scraper(seed='info.json')
distribution = metadata.distribution(latest=True, mediaType="text/csv",
                                     title=lambda x: "local authority greenhouse gas emissions dataset" in x)
metadata.dataset.title = distribution.title
metadata.dataset.comment = "UK local authority greenhouse gas emissions national ststistics."
metadata.dataset.description = """ 
These statistics provide a breakdown of greenhouse gas emissions 
across the UK, using nationally available datasets going back to 2005. This year we have 
included estimates of methane and nitrous oxide emissions in these statistics 
for the first time, in addition to the carbon dioxide emissions estimates 
which were published previously. Estimates of emissions within National Park areas 
have also been included in the statistics for the first time.

The main data sources are the UK National Atmospheric Emissions Inventory 
and the BEIS National Statistics of energy consumption for local authority 
areas. All emissions included in the national inventory are covered except 
those from aviation, shipping and military transport, for which there is no 
obvious basis for allocation to local areas, and emissions of fluorinated gases, 
for which suitable data are not available to estimate these emissions at a local 
level.
"""
# %%
df = distribution.as_pandas()
df.drop(columns=df.columns.values.tolist()[1:5], axis=1, inplace=True)

df.rename(columns={"Calendar Year": "Year",
                   "Greenhouse gas": "Greenhouse Gas",
                   "Territorial emissions (kt CO2e)": "Territorial emissions",
                   "CO2 emissions within the scope of influence of LAs (kt CO2e)": "Emissions within the scope of influence of LAs",
                   "Mid-year Population (thousands)": "Population",
                   "Area (km2)": "Area"}, inplace=True)

# %%
df["Territorial emissions per capita"] = df["Territorial emissions"]/df["Population"]
df["Territorial emissions per area"] = df["Territorial emissions"]/df["Area"]
df.replace([np.inf, -np.inf], 0, inplace=True)
for col in ['Territorial emissions', 'Emissions within the scope of influence of LAs',
            'Territorial emissions per capita', 'Territorial emissions per area']:
    df[col] = df[col].astype(str).astype(float).round(4)

df = pd.melt(df, id_vars=['Country', 'Local Authority', 'Local Authority Code', 'Year', 'LA GHG Sector', 'LA GHG Sub-sector', 'Greenhouse Gas'], value_vars=[
             "Territorial emissions", "Emissions within the scope of influence of LAs", 'Territorial emissions per capita', 'Territorial emissions per area'], var_name='Measure', value_name='Value')

df['Unit'] = df.apply(lambda x: 'kt CO2e' if x['Measure'] == 'Territorial emissions' else 'kt CO2e' if x['Measure'] == 'Emissions within the scope of influence of LAs' else 'tonnes of CO2e' if x['Measure']
                      == 'Territorial emissions per capita' else 'CO2e/m2' if x['Measure'] == 'Territorial emissions per area' else ' ', axis=1)
# %%
df['Value'] = df.apply(lambda x: 0 if np.isnan(
    x['Value']) else x['Value'], axis=1)
df = df.fillna('unallocated consumption')
df = df.drop_duplicates()
# %%
# Label : Large elec users (high voltage lines) unknown location
# notation : large-elec

# Unallocated consumption
# unallocated-consumption

# Unallocated electricity NI
# unallocated-elec-ni

df['Local Authority Code'] = df.apply(lambda x: 'unallocated-elec-ni' if x['Local Authority'] == 'Unallocated electricity NI' else 'unallocated-consumption' if x['Local Authority'] == 'Unallocated consumption' else 'large-elec' if x['Local Authority']
                                      == 'Large elec users (high voltage lines) unknown location' else x['Local Authority Code'], axis=1)
df = df[['Year', 'Country', 'Local Authority Code',
         'LA GHG Sector', 'LA GHG Sub-sector', 'Greenhouse Gas', 'Measure', 'Value', 'Unit']]

df = df.fillna('unallocated consumption')
df = df.drop_duplicates()

# Maping for local bespoke country codelist
df["Country"] = (
    df["Country"]
    .replace({
        "Unallocated": pathify("Unallocated"),
        "England": "E92000001",
        "Scotland": "S92000003",
        "Northern Ireland": "N92000002",
        "Wales": "W92000004",
    })
    .map(lambda x: (
        f"http://gss-data.org.uk/data/gss_data/climate-change/beis-2005-to-2020-local-authority-greenhouse-gas-emissions#concept/country/{x}" if x in [
            pathify("Unallocated"),
        ] else f"http://statistics.data.gov.uk/id/statistical-geography/{x}"
    ))
)
# Maping for local bespoke Local Authority codelist
df["Local Authority Code"] = (
    df["Local Authority Code"]
    .map(lambda x: (
        f"http://gss-data.org.uk/data/gss_data/climate-change/beis-2005-to-2020-local-authority-greenhouse-gas-emissions#concept/local-authority-code/{x}" if x in [
            ("large-elec"),
            ("unallocated-consumption"),
            ("unallocated-elec-ni")
        ] else f"http://statistics.data.gov.uk/id/statistical-geography/{x}"
    ))
)
df.rename(columns={'Local Authority Code': 'Local Authority'}, inplace=True)
# %%
df.to_csv('observations.csv', index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')
# %%
