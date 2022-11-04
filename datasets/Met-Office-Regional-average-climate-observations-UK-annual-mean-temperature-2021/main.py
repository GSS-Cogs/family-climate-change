import pandas as pd 
from gssutils import *
from csvcubed.models.cube.qb.catalog import CatalogMetadata

df = pd.read_csv("regional-average-climate-observations-uk-annual-mean-temperature.csv")

df['Measure Type'] = df.apply(
    lambda x: 'Annual Mean Temperature (Trend)' if 'trend' in x['Geography'] 
                else 'Annual Mean Temperature', axis=1)

df['Geography'] = df['Geography'].apply(lambda x: 'K02000001' if 'uk' in x
                                        else ('N92000002' if 'northern-ireland' in x
                                              else ('E92000001' if 'england' in x
                                                    else ('S92000003' if 'scotland' in x
                                                          else ('W92000004' if 'wales' in x else x)))))

df.to_csv('observations.csv', index=False)
catalog_metadata = CatalogMetadata(
    title="Regional annual average mean temperature with trends 1884 - 2021",
    creator_uri="https://www.gov.uk/government/organisations/the-meteorological-office",
    publisher_uri="https://www.gov.uk/government/organisations/met-office"
)
catalog_metadata.to_json_file('catalog-metadata.json')
