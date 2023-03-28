import pandas as pd
import json
from gssutils import *

info = json.load(open('info.json'))
title_id = info['id']

metadata = Scraper(seed="info.json")
metadata.dataset.title = "Domestic Energy Performance Certificates for new dwellings by energy efficiency rating 2022"
metadata.dataset.comment = "Data from certificates lodged on the Energy Performance of new Buildings Register by average energy efficiency rating."
metadata.dataset.description = "This data relates to the Energy Performance of Buildings Certificates published alongside the Energy Performance of Buildings Certificates Statistical release 26 January 2023."

distribution = [x for x in metadata.distributions if 'Table NB1' in x.title][0]
excluded = ['Cover_sheet', 'Notes', 'Table_of_contents']
tabs = [x for x in distribution.as_databaker() if x.name not in excluded]

dataframes = []
for tab in tabs:
    if tab.name in ["NB1", "NB1_England_Only", "NB1_Wales_Only"]:  
        year = tab.filter("Year").shift(0, 1).fill(
            DOWN) - tab.excel_ref("A77").expand(DOWN)
        quarter = tab.filter("Quarter").shift(
            0, 1).fill(DOWN) - tab.excel_ref("B77").expand(DOWN)
        lodgements = tab.filter("Number of Lodgements").shift(
            0, 1).fill(DOWN) - tab.excel_ref("C77").expand(DOWN)
        efficieny_rating = tab.filter("A").expand(RIGHT).is_not_blank() | tab.excel_ref("C4")
        observations = efficieny_rating.shift(0, 1).fill(DOWN).is_not_blank() - tab.excel_ref("J77") #There is an outlier on J77 on "NB1_England_Only" 
        if tab.name == "NB1":
            location = 'England and Wales'
        if tab.name == "NB1_England_Only":
            location = "E92000001"
        elif tab.name == "NB1_Wales_Only":
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

    elif tab.name in ["NB1_By_Region", "NB1_by_LA"]:
        if tab.name == "NB1_By_Region":
            location = tab.excel_ref("A15").expand(DOWN) - tab.excel_ref("A584").expand(DOWN)
            quarter =  tab.excel_ref("B15").expand(DOWN) - tab.excel_ref("B584").expand(DOWN)
            lodgements = tab.excel_ref("C15").expand(DOWN)- tab.excel_ref("B584").expand(DOWN)
            efficieny_rating = tab.filter("A").expand(RIGHT).is_not_blank() | tab.excel_ref("C4")
            observations = tab.excel_ref('E15').expand(
                    RIGHT).expand(DOWN).is_not_blank() | lodgements
        if tab.name == "NB1_by_LA":
            quarter = tab.filter("Quarter").fill(DOWN).is_not_blank() 
            location = tab.filter(
                "Local Authority Code").fill(DOWN).is_not_blank()
            lodgements = tab.filter("Number of Lodgements").fill(DOWN).is_not_blank() 
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
        return 'quarter/' + left(date, 4) + '-0' + right(date, 1)
    elif len(date) > 6:
        return 'quarter/' + left(date, 4) + '-0' + right(date, 1)
    else:
        return ""
    
df["Period"] = df["Period"].apply(date_time)
df = df.drop(["Year", "Quarter"], axis=1)

df['Location Label'] = df['Location'] # for creating labels on local codelist

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
    "Number of Lodgements": "Grand total"
}})

df['Efficiency Rating'] = df['Efficiency Rating'].apply(pathify)
# -
df['Measure Type'] = 'energy-performance-certificates'
df['Unit'] = 'Count'

df = df[['Period', 'Location', 'Efficiency Rating', 
         'Measure Type', 'Unit', 'Value']]

df = df.drop_duplicates()

df.to_csv('observations.csv', index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')