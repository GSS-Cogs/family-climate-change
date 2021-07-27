# +

import pandas as pd 
import json 
from pathlib import Path
# from typing import Union, Sequence, Any, List
# from unidecode import unidecode
from gssutils import *
# -

#

df = pd.read_csv("raw.csv")
df.drop(columns='daycount', axis=1, inplace=True)

df = pd.melt(df, id_vars=['period-start'])
df.rename(columns={'period-start': 'Year',
						'variable': 'Geography',
						'value': 'Rainfall'
						}, inplace=True)

df['Year'] = pd.to_datetime(df['Year']).dt.strftime('%Y')

df['Rainfall'] = df['Rainfall'].astype(str).astype(float).round(2)


out = Path('out')
out.mkdir(exist_ok=True)
df.to_csv(out/'monthly-rainfall.csv', index = False)

##No scraper present so we have created this manually 
from gssutils.csvw.mapping import CSVWMapping
with open('info.json') as f:
    info_json = json.load(f)
csvw_mapping = CSVWMapping()
csvw_mapping.set_mapping(info_json)
csvw_mapping.set_csv(out/"monthly-rainfall.csv")
csvw_mapping.set_dataset_uri(f"http://gss-data.org.uk/data/gss_data/climate-change/{info_json['id']}")
csvw_mapping.write(out/'rainfall.csv-metadata.json')

