# %%
import pandas as pd
from gssutils import *
from csvcubed.models.cube.qb.catalog import CatalogMetadata

df = pd.read_csv(
    "regional-average-climate-observations-uk-annual-rainfall.csv")
df

# %%
# map to measure type depending on what is in the geography column.
df['Measure Type'] = df.apply(
    lambda x: 'Rainfall (Trend)' if 'trend' in x['Geography'] else 'Rainfall', axis=1)

# %%
# map geography column to correct statistical codes depending on the country.
df['Geography'] = df['Geography'].apply(lambda x: 'K02000001' if 'uk' in x
                                        else ('N92000002' if 'northern-ireland' in x
                                              else ('E92000001' if 'england' in x
                                                    else ('S92000003' if 'scotland' in x
                                                          else ('W92000004' if 'wales' in x else x)))))
df
# %%
df.to_csv('observations.csv', index=False)
catalog_metadata = CatalogMetadata(
    title="Regional average climate observations, UK annual rainfall",
    summary="Data for the Regional annual average rainfall with trends 1836 - 2021",
    creator_uri="https://www.gov.uk/government/organisations/the-meteorological-office",
    publisher_uri="https://www.gov.uk/government/organisations/met-office",
    theme_uris=["https://www.ons.gov.uk/economy/environmentalaccounts"]
)
catalog_metadata.to_json_file('catalog-metadata.json')
