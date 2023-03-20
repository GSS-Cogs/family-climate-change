import pandas as pd
import json
from gssutils import *

info = json.load(open('info.json'))
title_id = info['id']

metadata = Scraper(seed="info.json")
metadata.dataset.title = "Domestic Energy Performance Certificates for existing dwellings by energy efficiency rating 2022"
metadata.dataset.comment = "Data from certificates lodged on the Energy Performance of existing Buildings Register by average energy efficiency rating."
metadata.dataset.description = "This data relates to the Energy Performance of Buildings Certificates published alongside the Energy Performance of Buildings Certificates Statistical release 26 January 2023."

distribution = [x for x in metadata.distributions if 'Table EB1' in x.title][0]
excluded = ['Cover_sheet', 'Notes', 'Table_of_contents']
tabs = [x for x in distribution.as_databaker() if x.name not in excluded]
dataframes = []
for tab in tabs:
    year = tab.filter("Year").shift(0, 1).expand(
        DOWN)  # refPeriod for all tabs
    quarter = tab.filter("Quarter").shift(
        0, 1).expand(DOWN)  # refPeriod for all tabs
    lodgements = tab.filter("Number of Lodgements").shift(
        0, 1).expand(DOWN)  # attribute for all tabs
    area = tab.filter("Total Floor Area (m2)").shift(
        0, 1).expand(DOWN)  # attribute for all tabs
    efficieny_rating = tab.filter("A").expand(RIGHT)  # dimension for all tabs

    if tab.name not in ["EB1_By_Region", "EB1_by_LA"]:
        observations = efficieny_rating.shift(0, 1).fill(DOWN).is_not_blank()
        if tab.name == "EB1":
            location = 'England and Wales'
        elif tab.name == "EB1_England_Only":
            location = "England"
        elif tab.name == "EB1_Wales_Only":
            location = "Wales"
        dimensions = [
            HDim(year, 'Year', DIRECTLY, LEFT),
            HDim(quarter, 'Quarter', DIRECTLY, LEFT),
            HDim(lodgements, 'Lodgements', DIRECTLY, LEFT),
            HDim(efficieny_rating, 'Efficiency Rating', DIRECTLY, ABOVE),
            HDim(area, 'Total Floor Area (m2)', DIRECTLY, LEFT),
            HDimConst('Location', location)
        ]
        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        df = tidy_sheet.topandas()
        dataframes.append(df)

    else:
        observations = efficieny_rating.fill(DOWN).is_not_blank()

        if tab.name == "EB1_By_Region":
            location = tab.filter("Region").shift(0, 1).expand(DOWN)
            observations = tab.excel_ref('E15').expand(
                RIGHT).expand(DOWN).is_not_blank()
        if tab.name == "EB1_by_LA":
            location = tab.filter(
                "Local Authority Code").shift(0, 1).expand(DOWN)

        dimensions = [
            HDim(quarter, 'Quarter', DIRECTLY, LEFT),
            HDim(lodgements, 'Lodgements', DIRECTLY, LEFT),
            HDim(efficieny_rating, 'Efficiency Rating', DIRECTLY, ABOVE),
            HDim(area, 'Total Floor Area (m2)', DIRECTLY, LEFT),
            HDim(location, 'Location', DIRECTLY, LEFT),
            HDimConst('Year', "")
        ]
        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        df = tidy_sheet.topandas()
        dataframes.append(df)
df = pd.concat(dataframes, sort=True)
df.rename(columns={'OBS': 'Value'}, inplace=True)
df['Year'] = df['Year'].astype(str).replace('\.0', '', regex=True)
df['Period'] = df['Quarter'] + df['Year']

# Format Date/Quarter
def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]

def date_time(date):
    if len(date) == 4:
        return 'year/' + date
    elif len(date) == 6:
        return 'quarter/' + left(date, 4) + '-0' + right(date, 1)
    else:
        return ""

df["Period"] = df["Period"].apply(date_time)
df = df.drop(["Year", "Quarter"], axis=1)

# df = df.replace({'Location': {
# "East Midlands": "http://data.europa.eu/nuts/code/UKF", #Check if we need uri
# "London": "http://data.europa.eu/nuts/code/UKI",
# "North East": "http://data.europa.eu/nuts/code/UKC",
# "North West": "http://data.europa.eu/nuts/code/UKD",
# "South East": "http://data.europa.eu/nuts/code/UKJ",
# "South West": "http://data.europa.eu/nuts/code/UKK",
# "East of England": "http://data.europa.eu/nuts/code/UKH",
# "West Midlands": "http://data.europa.eu/nuts/code/UKG",
# "Yorkshire and The Humber": "http://data.europa.eu/nuts/code/UKE",
# "Unknown": 'http://gss-data.org.uk/data/gss_data/climate-change/' +
# title_id + '#concept/local-authority-code/unknown',
# "England and Wales" : 'http://gss-data.org.uk/data/gss_data/climate-change/' +
# title_id + '#concept/local-authority-code/england-wales'
# }})

# info needed to create URI's for section
# sic = 'http://statistics.data.gov.uk/id/statistical-geography/'
# df['Location'] = df['Location'].map(
#     lambda x: sic + x if 'E0' in x else (sic + x if 'W0' in x else x))

df = df.replace({'Efficiency Rating': {
    "Not recorded": "Not Recorded",
    "not-recorded": 'Not Recorded'
}})
# -
df['Measure Type'] = 'energy-performance-certificates'
df['Unit'] = 'Count'
df = df[['Period', 'Efficiency Rating', 'Location', 'Lodgements',
         'Total Floor Area (m2)', 'Measure Type', 'Unit', 'Value']]

df.to_csv('observations.csv', index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')

# Creating a local codelist that fits the dataset
g = pd.DataFrame()
g["Label"] = df["Location"]

sic = 'http://statistics.data.gov.uk/id/statistical-geography/'
g["URI"] = (
    g["Label"]
    .replace({
        "England": "http://statistics.data.gov.uk/id/statistical-geography/E92000001",
        "Wales": "http://data.europa.eu/nuts/code/UKL",
        "East Midlands": "http://data.europa.eu/nuts/code/UKF",  # Check if we need uri
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
        "England and Wales": 'http://gss-data.org.uk/data/gss_data/climate-change/' +
        title_id + '#concept/local-authority-code/england-wales'
    })
    .map(lambda x: (
        sic + x if 'E0' in x else
        (sic + x if 'W0' in x else
         sic + x if 'E9' in x else
         sic + x if 'W9' in x
         else x)
    ))
)
g["Local Notation"] = g["URI"]
g["Parent URI"] = None

g["Sort Priority"] = None
g["Description"] = None

g.to_csv("./location.csv", index=False)