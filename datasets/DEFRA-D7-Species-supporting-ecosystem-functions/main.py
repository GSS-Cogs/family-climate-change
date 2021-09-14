# +
import json
import pandas as pd
from gssutils import *

df = pd.DataFrame()
cubes = Cubes('info.json')
info = json.load(open('info.json'))

metadata = Scraper(seed='info.json')
metadata.select_dataset(title = lambda x: "D7" in x)

distribution = metadata.distribution(latest=True)
title = distribution.title

df = distribution.as_pandas(encoding='ISO-8859-1')


# +
#Post Processing 
def left(s, amount):
    return s[:amount]
def right(s, amount):
    return s[-amount:]
def date_time (date):
    if len(date)  == 4:
        return date
    else: 
        date = date[date.find('(')+1:date.find(')')]
        return date
df['Year'] =  df["Year"].apply(date_time)

decimals = 1    
df['Value'] = df['Value'].apply(lambda x: round(x, decimals))

df['Series'] = df['Series'].apply(pathify)
df = df.fillna('not-applicable')
df['Trendline'] = df['Trendline'].apply(pathify)
df['Category'] = df['Category'].apply(pathify)
df
# -


metadata.dataset.title = distribution.title
metadata.dataset.family = 'climate-change'

cubes.add_cube(metadata, df, title)
cubes.output_all()
