# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.5
#   kernelspec:
#     display_name: Python 3.8.8 64-bit
#     name: python3
# ---

# ## Forestry-Research-Woodland-Area-Local-Authority

import json
import pandas as pd
from gssutils import *
from pathlib import Path
import shutil
from gssutils.csvw.mapping import CSVWMapping

df = pd.read_csv('raw.csv', skiprows=2, encoding='ISO-8859-1')

columns = df.columns.tolist()
df.dropna(subset=columns, inplace=True)
df.rename(columns={'Local_authority_Area' : 'Local Authority Area',
					'Standard_area_measurement _hectares' : 'Standard Area Measurement (hectares)',
					'Woodland_hectares' : 'Woodland (hectares)',
					'Woodland_%': 'Woodland %'
				}, inplace=True)

out = Path('out')
out.mkdir(exist_ok=True)
df.to_csv(out/'observations.csv', index = False)

# Metadata.json file is created manually as dataset was received as as raw csv file
with open('info.json') as f:
    info_json = json.load(f)
csvw_mapping = CSVWMapping()
csvw_mapping.set_mapping(info_json)
csvw_mapping.set_csv(out/'observations.csv')
csvw_mapping.set_dataset_uri(f"http://gss-data.org.uk/data/gss_data/climate-change/{info_json['id']}")
csvw_mapping.write(out/'observations.csv-metadata.json')

# metadata.trig file is created manually as dataset was received as as raw csv file
shutil.copy("observations.csv-metadata.trig", out/"observations.csv-metadata.trig")
