#%%
import json 
import pandas as pd 
from gssutils import *
from pathlib import Path
from csvcubed.models.cube.qb.catalog import CatalogMetadata

df = pd.read_csv("regional-average-climate-observations-uk-growing-season-length.csv")

##rename columns
#df.rename(columns={'Year' : 'Period'}, inplace=True)
#%%
#replace geography names with codes. Look for codes here: https://statistics.data.gov.uk/home 
df = df.replace({'Geography' : {
    "uk":"K02000001"
    ,"england":"E92000001"
    ,"wales":"W08000001" # this did come from W08 European Electoral Region so check with SB if suitable
    ,"scotland":"S04000001"
    ,"northern-ireland":"N07000001"
    ## waiting from feedback from SB on how to handle trends
    #,"uk-trend":"tbc"
    #,"england-trend":"tbc"
    #,"wales-trend":"tbc"
    #,"scotland-trend":"tbc"
    #,"northern-ireland-trend":"tbc"
    }}
)
#%%
#make output directory
out = Path('out')
out.mkdir(exist_ok=True)

#create observation file
df.to_csv(out/'regional-average-climate-observations-uk-growing-season-length.csv', index=False)

# ## No scraper present so we have create catalogue metadata manually
catalog_metadata = CatalogMetadata(
    title="Regional average climate observations UK growing season length 2021",
    summary="Regional average climate observations UK growing season length, 1960 - 2021",
    publisher_uri="https://www.gov.uk/government/organisations/met-office",
    theme_uris=[
        "https://uksa.statisticsauthority.gov.uk/themes/agriculture-energy-environment"],
    landing_page_uris=[
        "https://www.ons.gov.uk/economy/grossdomesticproductgdp/datasets/quarterlycountryandregionalgdp"],
    # dataset_issue="2022-09-29",
)
catalog_metadata.to_json_file(out/'catalog-metadata.json')

