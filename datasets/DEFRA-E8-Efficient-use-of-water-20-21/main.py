# DEFRA E8: Efficient use of water 20 - 21

import pandas as pd 
from gssutils import *
from csvcubed.models.cube.qb.catalog import CatalogMetadata

metadata = Scraper(seed='info.json')
metadata.select_dataset(title = lambda x: 'E8: Efficient use of water' in x)

distribution = metadata.distribution(mediaType='text/csv', latest=True)
df = distribution.as_pandas()

indexNames = df[df['Series'] == 'E8a'].index
df.drop(indexNames, inplace=True)
df.drop(columns=['Series'], inplace=True)

df['Year'] = df['Year'].str.replace(r'-20', r'-')
df['Year'] = df.apply(lambda x: 'government-year/' + x['Year'], axis = 1)
df = df.rename(columns={'Year' : 'Period'})
df['Value'] = pd.to_numeric(df['Value'], downcast='float')
df['Value'] = df['Value'].astype(str).astype(float).round(2)

df.to_csv('observations.csv', index=False) 
catalog_metadata = CatalogMetadata(
    title = "E8: Efficient use of water 20 - 21",
    summary = "Part of The Outcome Indicator Framework, a comprehensive set of indicators describing environmental change that relates to the 10 goals within the 25 Year Environment Plan. The framework contains 66 indicators, arranged into 10 broad themes. The indicators are extensive; they cover natural capital assets (for example, land, freshwater, air and seas) and together they show the condition of these assets, the pressures acting upon them and the provision of services or benefits they provide.",
)
catalog_metadata.to_json_file('catalog-metadata.json')
