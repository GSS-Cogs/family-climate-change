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

info = json.load(open('info.json'))
title_id = info['id']

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

df.columns

df.iloc[0:1]

# +
# df.drop(df.loc[df["Year"] == "Total"].index, inplace = True)
# df[~df["Year"].isin(["Total"])]
# -

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

second_list_df = pd.DataFrame(second_list_df)

type(second_list_df)

# +
# second_list_df[0:10, 4:12] = 0
# second_list_df[second_list_df.Quarter == 2008/4]
# -

second_list_df

# +
# stop
# -

second_list_df["Quarter"] = second_list_df["Quarter"].fillna("This row needs to be changed")
# second_list_df = second_list_df.loc[second_list_df["Quarter"] == np.nan, "Quarter"] = "This row needs to be changed"
# second_list_df["Quarter"] = second_list_df["Quarter"].map(lambda x: "This row needs to be changed" if x["Quarter"] == np.nan else x)

second_list_df["Quarter"].value_counts()

index = second_list_df[second_list_df["Quarter"] == "This row needs to be changed"].index

second_list_df.loc[index, ["A", "B", "C", "D", "E", "F", "G", "Not Recorded"]] = ''

# second_list_df = second_list_df.loc[second_list_df["Quarter"] == "This row needs to be changed", "Quarter"] = np.nan
index = second_list_df[second_list_df["Quarter"] == "This row needs to be changed"].index

second_list_df.loc[index, ["Quarter"]] = np.nan

second_list_df

second_list_df["Quarter"].value_counts()

type(second_list_df)

second_list_df.iloc[0:10, 4:12]

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

tidy.rename(columns = {"Quarter":"Period"}, inplace = True)
tidy

tidy = tidy[~tidy["Period"].isin(["Total"])]

tidy

tidy["Period"].unique()

tidy["Period"] =  tidy["Period"].astype(str).apply(lambda x: "year/" + x[:4] if len(x) == 4 else "quarter/" + x[:4] + "-0" + x[5:6] if len(x) == 6 else '')

tidy["Period"].unique()

tidy

tidy = tidy.replace({'Location': {
    "East Midlands": "http://data.europa.eu/nuts/code/UKF",
    "London": "http://data.europa.eu/nuts/code/UKI",
    "North East": "http://data.europa.eu/nuts/code/UKC",
    "North West": "http://data.europa.eu/nuts/code/UKD",
    "South East": "http://data.europa.eu/nuts/code/UKJ",
    "South West": "http://data.europa.eu/nuts/code/UKK",
    "East of England": "http://data.europa.eu/nuts/code/UKH",
    "West Midlands": "http://data.europa.eu/nuts/code/UKG",
    "Yorkshire and The Humber": "http://data.europa.eu/nuts/code/UKE",
    "Unknown": 'http://gss-data.org.uk/data/gss_data/climate-change/' +
    title_id + '#concept/local-authority-code/unknown',
    "England and Wales" : 'http://gss-data.org.uk/data/gss_data/climate-change/' +
    title_id + '#concept/local-authority-code/england-wales'
}})

sic = 'http://statistics.data.gov.uk/id/statistical-geography/'
tidy['location'] = tidy['location'].map(
    lambda x: sic + x if 'E0' in x else (  sic + x if 'W0' in x else x))

tidy = tidy.replace({'Efficieny Rating': {
    "Not recorded": "Not Recorded",
    "not-recorded": 'Not Recorded'
    }})

tidy['Measure Type'] = 'energy-performance-certificates'
tidy['Unit'] = 'count'
# tidy = tidy[['Period', 'Efficieny Rating', 'Location', 'Lodgements', 'Total Floor Area (m2)','Measure Type', 'Unit', 'Value']]

tidy.columns

tidy = tidy[['Period', 'Number of Lodgements', 'Total Floor Area (m2)', 'location',
       'Efficieny Rating', 'value', 'Measure Type', 'Unit']]

tidy.to_csv('observations.csv', index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')
