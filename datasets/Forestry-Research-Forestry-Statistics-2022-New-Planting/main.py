# %%
import pandas as pandas
from gssutils import *
import pandas as pd
from csvcubed.models.cube.qb.catalog import CatalogMetadata

df = pd.read_excel("NPRS-machinereadable-16jun22.ods", sheet_name='C11', skiprows=4,  usecols=[
                   "Year", "Broadleaves Total (thousand ha)", "Conifers Total (thousand ha)", "United Kingdom Total (thousand ha) [note 3]"], engine="odf")

df = pd.melt(frame=df, id_vars=['Year'],
             var_name='Measure Type', value_name='Value').dropna()
df['Marker'] = df['Year'].str.split(" ").str[1]
# [r] = revised, [p] = provisional, [z] = not applicable
df = df.replace({'Marker': {"[r]": "revised", "[p]": "provisional",
                            "[z]": "not-applicable"}})
df['Year'] = df['Year'].astype('str')
df['Year'] = df['Year'].str[:4]
df['Measure Type'] = df['Measure Type'].str.replace(
    r"\(.*?\)", "", regex=True).str.rstrip().str.strip("[note 3]").str.strip("United Kingdom ")
df = df.replace({'Measure Type': {"Conifers Total": "new-conifers", "Broadleaves Total": "new-broadleaves",
                                  "Total": "total-new"}})
df['Unit'] = 'thousand-hectares'
df['Value'] = df['Value'].round(2)
# %%
df.to_csv("observations.csv", index=False)
# %%
# Total : Includes woodland formed by natural colonisation (where known).
catalog_metadata = CatalogMetadata(
    title="Forestry Statistics 2022 New Planting",
    summary="New planting in the United Kingdom, 1971 - 2022",
    publisher_uri="https://www.gov.uk/government/organisations/forest-research",
    theme_uris=[
        "https://uksa.statisticsauthority.gov.uk/themes/agriculture-energy-environment"],
    landing_page_uris=[
        "https://www.forestresearch.gov.uk/tools-and-resources/statistics/data-downloads/"],
    # dataset_issue="2022-09-29",
)
catalog_metadata.to_json_file('catalog-metadata.json')
