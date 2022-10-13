#         DEFRA-UK-WATER-LEAKAGE-20-21

import pandas as pd 
from gssutils import *

metadata = Scraper(seed='info.json')
metadata.select_dataset(title = lambda x: 'E8: Efficient use of water' in x)

metadata.dataset.family = 'climate-change'
metadata.dataset.title = "UK Water Leakage 20 - 21"

distribution = metadata.distribution(mediaType='text/csv', latest=True)
df = distribution.as_pandas()

indexNames = df[df['Series'] == 'E8b'].index
df.drop(indexNames, inplace=True)
df.drop(columns=['Series'], inplace=True)

df['Year'] = df['Year'].str.replace(r'-20', r'-') 
df = df.rename(columns={'Year' : 'Period'})
df['Value'] = pd.to_numeric(df['Value'], downcast='float')
df['Value'] = df['Value'].astype(str).astype(float).round(2)

df.to_csv('observations.csv', index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')
