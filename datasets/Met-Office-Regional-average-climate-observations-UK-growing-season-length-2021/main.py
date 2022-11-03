#%%
import json 
import pandas as pd 
from gssutils import *
from pathlib import Path
from csvcubed.models.cube.qb.catalog import CatalogMetadata

df = pd.read_csv("regional-average-climate-observations-uk-growing-season-length.csv")

# add measure type column to differentiate between actual value and trend value
df['Measure Type'] = df.apply(lambda x: 'Annual Growing Season Length (Trend)' if 'trend' in x['Geography'] else 'Annual Growing Season Length', axis=1)

##rename columns
#df.rename(columns={'Year' : 'Period'}, inplace=True)
#%%
#replace geography names with codes. Look for codes here: https://statistics.data.gov.uk/home 
df = df.replace({'Geography' : {
    "uk":"K02000001"
    ,"england":"E92000001"
    ,"wales":"W92000004" # this did come from W08 European Electoral Region so check with SB if suitable
    ,"scotland":"S04000001"
    ,"northern-ireland":"N92000002"
    ,"uk-trend":"K02000001"
    ,"england-trend":"E92000001"
    ,"wales-trend":"W92000004"
    ,"scotland-trend":"S04000001"
    ,"northern-ireland-trend":"N92000002"
    }}
)


#%%
#make output directory
out = Path('out')
out.mkdir(exist_ok=True)

#create observation file
df.to_csv(out/'observations.csv', index=False)

# ## No scraper present so we have create catalogue metadata manually
catalog_metadata = CatalogMetadata(
    title="Regional average climate observations UK growing season length 2021",
    summary="Regional average climate observations UK growing season length, 1960 - 2021",
    publisher_uri="https://www.gov.uk/government/organisations/met-office",
    # dataset_issue="2022-09-29",
)
catalog_metadata.to_json_file(out/'catalog-metadata.json')

