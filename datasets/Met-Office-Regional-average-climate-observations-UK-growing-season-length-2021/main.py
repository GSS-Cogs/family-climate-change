#%%
import json 
import pandas as pd 
from gssutils import *
from pathlib import Path
import shutil
from gssutils.csvw.mapping import CSVWMapping

df = pd.read_csv("regional-average-climate-observations-uk-growing-season-length.csv")

#rename columns
df.rename(columns={'Year' : 'Period'}, inplace=True)

#make output directory
out = Path('out')
out.mkdir(exist_ok=True)

#create observation file
df.to_csv(out/'regional-average-climate-observations-uk-growing-season-length.csv', index=False)

# ## No scraper present so we have create catalogue metadata manually
with open('info.json') as f:
    info_json = json.load(f)
csvw_mapping = CSVWMapping()
csvw_mapping.set_mapping(info_json)
csvw_mapping.set_csv(out/'regional-average-climate-observations-uk-growing-season-length.csv')
csvw_mapping.set_dataset_uri(f"http://gss-data.org.uk/data/gss_data/climate-change/{info_json['id']}")
csvw_mapping.write(out/'regional-average-climate-observations-uk-growing-season-length.csv-metadata.json')

shutil.copy("regional-average-climate-observations-uk-growing-season-length.csv-metadata.trig", out/"regional-average-climate-observations-uk-growing-season-length.csv-metadata.trig")



