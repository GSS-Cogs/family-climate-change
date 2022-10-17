#         DEFRA-UK-WATER-LEAKAGE-20-21

import pandas as pd 
from gssutils import *

metadata = Scraper(seed='info.json')
metadata.select_dataset(title = lambda x: 'E8: Efficient use of water' in x)

metadata.dataset.family = 'climate-change'
metadata.dataset.title = "UK Water Leakage 20 - 21"
metadata.dataset.description = """
Climate change and a growing population will put increasing pressure on our water supplies.
Ambitious reductions in water leakage have a significant role in maintaining secure supplies and protecting the environment. 
This indicator shows changes in the efficient use of water, focussing on leakage. 
Leakage of water in England are existing metrics reported to The Water Services Regulation Authority (Ofwat) and the Environment Agency.
"""

distribution = metadata.distribution(mediaType='text/csv', latest=True)
df = distribution.as_pandas()

indexNames = df[df['Series'] == 'E8b'].index
df.drop(indexNames, inplace=True)
df.drop(columns=['Series'], inplace=True)

df['Year'] = df['Year'].str.replace(r'-20', r'-')
df['Value'] = pd.to_numeric(df['Value'], downcast='float')
df['Value'] = df['Value'].astype(str).astype(float).round(2)

df.to_csv('observations.csv', index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')
