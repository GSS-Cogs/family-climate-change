import json 
import pandas as pd 
from gssutils import *
from pathlib import Path
import shutil
from gssutils.csvw.mapping import CSVWMapping

df = pd.read_csv("raw.csv")
#df.drop(columns='daycount', axis=1, inplace=True)

df = pd.melt(df, id_vars=['Year'])
df.rename(columns={'value': 'Value',
                   'variable':'Measure Type'

                }, inplace=True)

df['Units'] = 'thousand-hectares'             

#df['Month'] = pd.to_datetime(df['Month'], dayfirst=True).dt.strftime('%Y-%m')

#df['Geography'].replace({'ondon': 'london'}, inplace=True)
df['Measure Type'] = df['Measure Type'].apply(pathify)
#df['Year'] = df['Year'].astype(str)
#df['Rainfall'] = df['Rainfall'].astype(str).astype(float).round(2)

out = Path('out')
out.mkdir(exist_ok=True)
df.to_csv(out/'new-planting.csv', index = False)

# ## No scraper present so we have created this manually

# +
with open('info.json') as f:
    info_json = json.load(f)
csvw_mapping = CSVWMapping()
csvw_mapping.set_mapping(info_json)
csvw_mapping.set_csv(out/"new-planting.csv")
csvw_mapping.set_dataset_uri(f"http://gss-data.org.uk/data/gss_data/climate-change/{info_json['id']}")
csvw_mapping.write(out/'new-planting.csv-metadata.json')

shutil.copy("new-planting.csv-metadata.trig", out/"new-planting.csv-metadata.trig")


