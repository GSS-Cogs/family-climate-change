import pandas as pd
import json
from gssutils import *

info = json.load(open('info.json'))
title_id = info['id']

metadata = Scraper(seed="info.json")
metadata.dataset.title = "Domestic Energy Performance Certificates for existing dwellings by energy efficiency rating (updated)"
metadata.dataset.comment = "Data from certificates for existing domestic properties lodged on the Energy Performance of Buildings Registers, by average energy efficiency rating."
metadata.dataset.issued = "2023-05-03T13:48:45.403621+00:00"
metadata.dataset.description = """
This data relates to the Energy Performance of Buildings Certificates published alongside the Energy Performance of Buildings Certificates Statistical release.
The data is drawn from certificates for existing domestic properties lodged on the Energy Performance of Buildings Registers since 2008, including average energy efficiency ratings and numbers of certificates recorded.

The Energy Performance Certificates (EPC) register does not hold data for every domestic and non-domestic building or every building occupied by public authorities in England and Wales. 
Buildings only require an EPC when, sold, let or constructed.  These statistics should, therefore, not be interpreted as a true representation of the whole of the building stock in England and Wales, but viewed as part of a wider package of Government’s provision of information on the energy efficiency of buildings. 
"""

distribution = [x for x in metadata.distributions if 'Table EB1' in x.title][0]
excluded = ['Cover_sheet', 'Notes', 'Table_of_contents']
tabs = [x for x in distribution.as_databaker() if x.name not in excluded]

dataframes = []
for tab in tabs:
    if tab.name in ["EB1_England_and_Wales", "EB1_England_Only", "EB1_Wales_Only"]:   
        year = tab.filter("Year").shift(0, 1).fill(
            DOWN)
        quarter = tab.filter("Quarter").shift(
            0, 1).fill(DOWN) 
        efficieny_rating = tab.filter("A").expand(RIGHT).is_not_blank() | tab.excel_ref("C4")
        observations = efficieny_rating.shift(0, 1).fill(DOWN).is_not_blank()
        if tab.name == "EB1_England_and_Wales":
            location = 'England and Wales'
        elif tab.name == "EB1_England_Only":
            location = "E92000001"
        elif tab.name == "EB1_Wales_Only":
            location = "W92000004"
        dimensions = [
            HDim(year, 'Year', DIRECTLY, LEFT),
            HDim(quarter, 'Quarter', DIRECTLY, LEFT),
            HDim(efficieny_rating, 'Efficiency Rating', DIRECTLY, ABOVE),
            HDimConst('Location', location)
        ]
        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        df = tidy_sheet.topandas()
        dataframes.append(df)
        print(tab.name)

    elif tab.name in ["EB1_by_Region", "EB1_by_LA"]:
        if tab.name == "EB1_by_Region":
            location = tab.excel_ref("A15").expand(DOWN) 
            quarter =  tab.excel_ref("B15").expand(DOWN) 
            efficieny_rating = tab.filter("A").expand(RIGHT).is_not_blank() | tab.excel_ref("C4")
            observations = efficieny_rating.shift(0, 14).fill(DOWN)
        elif tab.name == "EB1_by_LA":
            quarter = tab.filter("Quarter").fill(DOWN)
            location = tab.filter(
                "Local Authority Code").fill(DOWN)
        
            efficieny_rating = tab.filter("A").expand(RIGHT).is_not_blank() | tab.excel_ref("D4")
            observations = efficieny_rating.fill(DOWN).is_not_blank()

        dimensions = [
            HDim(quarter, 'Quarter', DIRECTLY, LEFT),
            HDim(efficieny_rating, 'Efficiency Rating', DIRECTLY, ABOVE),
            HDim(location, 'Location', DIRECTLY, LEFT),
            HDimConst('Year', "")
        ]
        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        df = tidy_sheet.topandas()
        dataframes.append(df)
        print(tab.name)

df = pd.concat(dataframes, sort=True)
df.rename(columns={'OBS': 'Value'}, inplace=True)
df['Value'] = df['Value'].astype(int)
df['Period'] = df['Year'] + df['Quarter'] 

# Format Date/Quarter
def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]

def date_time(date):
    if len(date) == 4:
        return 'year/' + date
    elif len(date) == 6:
        return 'quarter/' + left(date, 4) + '-Q' + right(date, 1)
    elif len(date) > 6:
        return 'quarter/' + left(date, 4) + '-Q' + right(date, 1)
    else:
        return ""

df["Period"] = df["Period"].apply(date_time)
df = df.drop(["Year", "Quarter"], axis=1)

df = df.replace({'Location': {
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
title_id + '-concept/local-authority-code/unknown',
"England and Wales" : 'http://gss-data.org.uk/data/gss_data/climate-change/' +
title_id + '-concept/local-authority-code/england-wales'
}})

# info needed to create URI's for LA codes
sic = 'http://statistics.data.gov.uk/id/statistical-geography/'
df['Location'] = df['Location'].map(lambda x: 
        sic + x if 'E0' in x else
        sic + x if 'W0' in x else
        sic + x if 'E9' in x else
        sic + x if 'W9' in x
        else x
)

df = df.replace({'Efficiency Rating': {
    "Not recorded": "Not Recorded",
    "not-recorded": 'Not Recorded',
    "Number Lodgements": "Total Efficiency Rating"
}})

df['Efficiency Rating'] = df['Efficiency Rating'].apply(pathify)

df = df[['Period', 'Location', 'Efficiency Rating', 
        'Value']]

#The EB1 certificates for 'Unknown' regions (EB1_By_Region) are repeated for 'Unknown' LA (EB1_by_LA)
df = df.drop_duplicates()

df.to_csv('observations.csv', index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')