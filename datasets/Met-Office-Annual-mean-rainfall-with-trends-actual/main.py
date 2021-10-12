import json 
import pandas as pd 
from gssutils import *
from pathlib import Path
import shutil
from gssutils.csvw.mapping import CSVWMapping

df = pd.read_csv("raw.csv")
#df.drop(columns='daycount', axis=1, inplace=True)

df = pd.melt(df, id_vars=['Year'])
df.rename(columns={
                'variable': 'Geography',
                'value': 'Value'
                }, inplace=True)

#df['Month'] = pd.to_datetime(df['Month'], dayfirst=True).dt.strftime('%Y-%m')

#df['Geography'].replace({'ondon': 'london'}, inplace=True)
df['Geography'] = df['Geography'].apply(pathify)
#df['Rainfall'] = df['Rainfall'].astype(str).astype(float).round(2)

out = Path('out')
out.mkdir(exist_ok=True)
df.to_csv(out/'rainfall.csv', index = False)

# ## No scraper present so we have created this manually

# +
with open('info.json') as f:
    info_json = json.load(f)
csvw_mapping = CSVWMapping()
csvw_mapping.set_mapping(info_json)
csvw_mapping.set_csv(out/"rainfall.csv")
csvw_mapping.set_dataset_uri(f"http://gss-data.org.uk/data/gss_data/climate-change/{info_json['id']}")
csvw_mapping.write(out/'rainfall.csv-metadata.json')

shutil.copy("rainfall.csv-metadata.trig", out/"rainfall.csv-metadata.trig")


