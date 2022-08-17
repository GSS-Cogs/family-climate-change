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
df1

df1["location"] = "England and Wales"
df1

df2 = pd.DataFrame(multi_lists[1])
df2

df2["location"] = "http://statistics.data.gov.uk/id/statistical-geography/E92000001"
df2

df3 = pd.DataFrame(multi_lists[2])
df3

df3["location"] = "http://data.europa.eu/nuts/code/UKL"
df3

df = pd.concat([df1,df2, df3])
# df = pd.concat([df1,df2])

df

df.Quarter.fillna(df.Year, inplace = True)
del df["Year"]
# df.rename(columns={'Not  Recorded': 'Not Recorded'}, inplace=True)
df

# +
#Completed first three tabs
# -

df.columns
# 'Not Recorded'
# 'Not Recorded'

df["Not  Recorded"].value_counts()

df["Not Recorded"] = df["Not Recorded"].fillna(df.pop("Not  Recorded"))
df

df["Not Recorded"].value_counts()

df.columns

# +
# efficiency_rating

frame1 = pd.melt(df, id_vars = ['Quarter', 'Number of Lodgements', 'Total Floor Area (m2)', 'location'], value_vars = ['A', 'B',
       'C', 'D', 'E', 'F', 'G', 'Not Recorded'], var_name = "Efficieny Rating", ignore_index=False)
# -

frame1

second_list_df = pd.read_excel(distribution.downloadURL, sheet_name = "NB1_By_Region", header = 3)
second_list_df

type(second_list_df)

second_list_df.rename(columns = {"Region":"location"}, inplace = True)

second_list_df

# +
# efficiency_rating

frame2 = pd.melt(second_list_df, id_vars = ['Quarter', 'Number of Lodgements', 'Total Floor Area (m2)', 'location'], value_vars = ['A', 'B',
       'C', 'D', 'E', 'F', 'G', 'Not Recorded'], var_name = "Efficieny Rating", ignore_index=False)
# -

frame2

third_list_df = pd.read_excel(distribution.downloadURL, sheet_name = "NB1_By_LA", header = 3)
third_list_df

third_list_df.drop(["Local Authority"], axis = 1, inplace = True)

third_list_df

third_list_df.rename(columns = {"Local Authority Code":"location"}, inplace = True)

third_list_df

# +
# efficiency_rating

frame3 = pd.melt(third_list_df, id_vars = ['Quarter', 'Number of Lodgements', 'Total Floor Area (m2)', 'location'], value_vars = ['A', 'B',
       'C', 'D', 'E', 'F', 'G', 'Not Recorded'], var_name = "Efficieny Rating", ignore_index=False)
# -

frame3

frames = [frame1, frame2, frame3]

tidy = pd.concat(frames).fillna('')

tidy.rename(columns = {"Quarter":"period"}, inplace = True)
tidy


