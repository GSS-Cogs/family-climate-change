#%%
import re
import pandas as pd 
import json 
from pathlib import Path
from typing import Union, Sequence, Any, List
from unidecode import unidecode

#%%
def pathify(label):
    """
      Convert a label into something that can be used in a URI path segment.
    """
    return re.sub(r'-$', '',
                  re.sub(r'-+', '-',
                         re.sub(r'[^\w/]', '-', unidecode(label).lower())))



pd.melt(rainfall, id_vars=['period-start'])




#%%
rainfall["period_start"]= rainfall["period_start"].astype(str).apply(pathify) 
rainfall["east scotland"]= rainfall["east scotland"].astype(str).apply(pathify) 
rainfall["north scotland"]= rainfall["north scotland"].astype(str).apply(pathify) 
rainfall["west scotland"]= rainfall["west scotland"].astype(str).apply(pathify) 
rainfall["northern ireland"]= rainfall["northern ireland"].astype(str).apply(pathify) 
rainfall["east midlands"]= rainfall["east midlands"].astype(str).apply(pathify) 
rainfall["east of england"]= rainfall["east of england"].astype(str).apply(pathify) 
rainfall["london"]= rainfall["london"].astype(str).apply(pathify) 
rainfall["north east england"]= rainfall["north east england"].astype(str).apply(pathify) 
rainfall["north west england"]= rainfall["north west england"].astype(str).apply(pathify) 
rainfall["south east england"]= rainfall["south east england"].astype(str).apply(pathify) 
rainfall["south west england"]= rainfall["south west england"].astype(str).apply(pathify) 
rainfall["wales"]= rainfall["wales"].astype(str).apply(pathify) 
rainfall["west midlands"]= rainfall["west midlands"].astype(str).astype(str).apply(pathify) 
rainfall["daycount"]= rainfall["daycount"].astype(str).apply(pathify) 

#%%
rainfall = pd.read_csv("raw.csv")


rainfall = rainfall.drop(columns='daycount')

rainfall = pd.melt(rainfall, id_vars=['period-start'])

rainfall.to_csv("monthly-rainfall.csv",index = False) 



# %%
##No scraper present so we have created this manually 
from gssutils.csvw.mapping import CSVWMapping
with open('info.json') as f:
    info_json = json.load(f)
csvw_mapping = CSVWMapping()
csvw_mapping.set_mapping(info_json)
csvw_mapping.set_csv(Path("monthly-rainfall.csv"))
csvw_mapping.set_dataset_uri(f"http://gss-data.org.uk/data/gss_data/climate-change/{info_json['id']}")
csvw_mapping.write(Path("rainfall.csv-metadata.json"))
# %%
