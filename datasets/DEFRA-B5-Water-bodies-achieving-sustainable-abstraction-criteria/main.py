# +
import json
import pandas as pd
from gssutils import *

df = pd.DataFrame()
cubes = Cubes('info.json')
info = json.load(open('info.json'))

metadata = Scraper(seed='info.json')
metadata.select_dataset(title = lambda x: "B5" in x)
metadata.dataset.family = 'climate-change'

distribution = metadata.distribution(latest=True)
title = distribution.title
# -

df = distribution.as_pandas(encoding='ISO-8859-1')
#Post Processing 
df['Year'] = df['Year'].astype(str)
df['Year'] = 'year/' + df['Year']
df['Water body category'] = df['Water body category'].apply(pathify)
df

cubes.add_cube(metadata, df, title)
cubes.output_all()
