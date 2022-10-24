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
# Maping for local bespoke country codelist
df["Country"] = (
    df["Country"]
    .replace({
        "UK": "K02000001",
        "England": "E92000001",
        "Scotland": "S92000003",
        "Northern Ireland": "N92000002",
        "Wales": "W92000004",
    })
    .map(lambda x: (
        f"http://statistics.data.gov.uk/id/statistical-geography/{x}"
    ))
)

df.to_csv("observations.csv", index=False)
catalog_metadata = CatalogMetadata(
    title="Forestry Statistics 2022 Woodland Area",
    summary="Woodland area by country since 1998.",
    publisher_uri="https://www.gov.uk/government/organisations/forest-research",
    theme_uris=[
        "https://uksa.statisticsauthority.gov.uk/themes/agriculture-energy-environment"],
    landing_page_uris=[
        "https://www.forestresearch.gov.uk/tools-and-resources/statistics/forestry-statistics/forestry-statistics-2022/1-woodland-area-planting/"],
    # dataset_issue="2022-09-29",
    description=""" 
Woodland is defined in UK forestry statistics as land under stands of trees with a
minimum area of 0.5 hectares and a canopy cover of at least 20%, or having the
potential to achieve this. The definition relates to land use, rather than land cover,
so integral open space and felled areas that are awaiting restocking are included as
woodland. Further information, including how this UK definition compares with the
international definition of woodland, is provided in the Sources chapter.
Statistics on woodland area are used to inform government policy and resource
allocation, to provide context to UK forestry and land management issues and are
reported to international organisations. They are also used in the compilation of
natural capital accounts.
Increases in woodland area result from the creation of new woodland. This can be
achieved through new planting or by natural colonisation of trees. Further
information is available https://cdn.forestresearch.gov.uk/2022/09/Ch1_Woodland_2022.pdf
    """,
)

catalog_metadata.to_json_file('catalog-metadata.json')
# %%
