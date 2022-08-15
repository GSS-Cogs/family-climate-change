# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.8
#   kernelspec:
#     display_name: Python 3.9.13 64-bit
#     language: python
#     name: python3
# ---

from gssutils import *
import json
import pandas as pd
import numpy as np

metadata = Scraper(seed="info.json")
distribution = metadata.distribution(title = lambda x: "Table NB1" in x)

distribution

df = pd.read_excel(distribution.downloadURL, sheet_name = ["NB1", "NB1_England_Only", "NB1_Wales_Only"], header = 3)
df

df

type(df)

# +
# df.columns
# -

df = df.values()

df

multi_lists = [x for x in df]


multi_lists[0]

multi_lists[1]

df1 = pd.DataFrame(multi_lists[0])
# type(df1)
# len(df)

# +
# df
# -

df2 = pd.DataFrame(multi_lists[1])
df2

df3 = pd.DataFrame(multi_lists[2])
df3

df = pd.concat([df1,df2, df3])

df

df.Quarter.fillna(df.Year, inplace = True)
del df["Year"]
df

# +
#Completed first three tabs
# -


