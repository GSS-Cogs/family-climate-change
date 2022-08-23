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

df.drop(df.loc[df["Year"] == "Total"].index, inplace = True)
df = df[~df["Year"].isin(["Total"])]

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

# +
# df["Not  Recorded"].value_counts()
# -

#get rid of "Not  Recorded" while keeping "Not Recorded" column
df["Not Recorded"] = df["Not Recorded"].fillna(df.pop("Not  Recorded"))
df

# +
# df["Not Recorded"].unique()

# +
# df["Not Recorded"].value_counts()
# -

df.columns

# +
# efficiency_rating

frame1 = pd.melt(df, id_vars = ['Quarter', 'Number of Lodgements', 'Total Floor Area (m2)', 'location'], value_vars = ['A', 'B',
       'C', 'D', 'E', 'F', 'G', 'Not Recorded'], var_name = "Efficieny Rating", ignore_index=False)
# -

frame1

second_list_df = pd.read_excel(distribution.downloadURL, sheet_name = "NB1_By_Region", header = 3)
second_list_df

df2 = second_list_df.drop(second_list_df.index[0:10])

df2

df2.rename(columns = {"Region":"location"}, inplace = True)

# +
# efficiency_rating

frame2 = pd.melt(df2, id_vars = ['Quarter', 'Number of Lodgements', 'Total Floor Area (m2)', 'location'], value_vars = ['A', 'B',
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
# .drop_duplicates()

tidy.rename(columns = {"Quarter":"Period"}, inplace = True)
tidy

tidy = tidy[~tidy["Period"].isin(["Total"])]

tidy


# +
# tidy["Period"] =  tidy["Period"].astype(str).apply(lambda x: "year/" + x[:4] if len(x) == 4 else "quarter/" + x[:4] + "-0" + x[5:6] if len(x) == 6 else np.nan)

#Format Date/Quarter
def left(s, amount):
    return s[:amount]
def right(s, amount):
    return s[-amount:]
def date_time(date):
    if len(date)  == 4:
        return 'year/' + date
    elif len(date) == 6:
        return 'quarter/' + left(date,4) + '-0' + right(date,1)
    else:
        return ''


# -

tidy["Period"] =  tidy["Period"].astype(str).apply(date_time)

tidy

tidy = tidy.replace({'location': {
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

tidy.rename(columns = {"Number of Lodgements" : "Lodgements", "location" : "Location", "value": "Value"}, inplace = True, errors = "raise")

tidy = tidy[['Period', 'Lodgements', 'Total Floor Area (m2)', 'Location',
       'Efficieny Rating', 'Value', 'Measure Type', 'Unit']]

tidy

tidy.columns

badTidy = tidy[tidy.duplicated(['Period', 'Value', 'Lodgements', 'Total Floor Area (m2)', 'Location',
       'Efficieny Rating', 'Measure Type', 'Unit'], keep = False)]

badTidy.sort_values(by = ['Period', 'Value', 'Lodgements', 'Total Floor Area (m2)', 'Location',
       'Efficieny Rating', 'Measure Type', 'Unit']).to_csv("badTidy.csv")

print(0.0 in badTidy["Value"].values)

tidy

# +
# tidy = tidy.drop_duplicates()
# -

tidy

tidy.columns

print('' in tidy["Period"].unique())

# +
# n = 0
# for x in tidy["Period"]:
#     if x == '':
#         n += 1
#         print(n, x)
# -

print('' in tidy["Lodgements"].unique())

print('' in tidy["Total Floor Area (m2)"].unique())

print('' in tidy["Location"].unique())

print('' in tidy["Efficieny Rating"].unique())

print('' in tidy["Value"].unique())

n = 0
for x in tidy["Value"]:
    if x == '':
        n += 1
        print(n, x)

# +
# tidy.loc[tidy["Value"] == ''] = "Not applicable"

# +
# n = 0
# for x in tidy["Value"]:
#     if x == '':
#         n += 1
#         print(n, x)
# -

print('' in tidy["Value"].unique())

# +
# badTidy = tidy[tidy.duplicated(['Period', 'Lodgements', 'Total Floor Area (m2)', 'Location',
#        'Efficieny Rating', 'value', 'Measure Type', 'Unit', 'sheet'], keep = False)]

# +
# badTidy
# -

tidy

tidy.to_csv('observations.csv', index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')
