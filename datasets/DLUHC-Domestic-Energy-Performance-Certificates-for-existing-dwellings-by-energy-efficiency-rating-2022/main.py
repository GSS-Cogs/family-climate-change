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
    if tab.name in ["EB1", "EB1_England_Only", "EB1_Wales_Only"]:   #["EB1_By_Region", "EB1_by_LA"]:
        # efficieny_rating = tab.filter("A").expand(RIGHT).is_not_blank() + tab.excel_ref("C4")
        year = tab.filter("Year").shift(0, 1).fill(
            DOWN) - tab.excel_ref("A77").expand(DOWN)
        quarter = tab.filter("Quarter").shift(
            0, 1).fill(DOWN) - tab.excel_ref("B77").expand(DOWN)
        # lodgements = tab.filter("Number of Lodgements").shift(
        #     0, 1).fill(DOWN) - tab.excel_ref("C77").expand(DOWN)
        efficieny_rating = tab.filter("A").expand(RIGHT).is_not_blank()
        observations = efficieny_rating.shift(0, 1).fill(DOWN).is_not_blank()
        if tab.name == "EB1":
            location = 'England and Wales'
        if tab.name == "EB1_England_Only":
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

    elif tab.name in ["EB1_By_Region", "EB1_by_LA"]:
        if tab.name == "EB1_By_Region":
            location = tab.excel_ref("A15").expand(DOWN) - tab.excel_ref("A584").expand(DOWN)
            quarter =  tab.excel_ref("B15").expand(DOWN) - tab.excel_ref("B584").expand(DOWN)
            # lodgements = tab.excel_ref("C15").expand(DOWN)- tab.excel_ref("B584").expand(DOWN)
            efficieny_rating = tab.filter("A").expand(RIGHT).is_not_blank() 
            observations = tab.excel_ref('E15').expand(
                    RIGHT).expand(DOWN).is_not_blank()
        if tab.name == "EB1_by_LA":
            quarter = tab.filter("Quarter").fill(DOWN).is_not_blank() 
            location = tab.filter(
                "Local Authority Code").fill(DOWN).is_not_blank()
            # lodgements = tab.filter("Number of Lodgements").fill(DOWN).is_not_blank() 
            efficieny_rating = tab.filter("A").expand(RIGHT).is_not_blank()
            observations = efficieny_rating.fill(DOWN).is_not_blank()

        dimensions = [
            HDim(quarter, 'Quarter', DIRECTLY, LEFT),
            # HDim(lodgements, 'Lodgements', DIRECTLY, LEFT),
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
df['Year'] = df['Year'].astype(str).replace('\.0', '', regex=True)
df['Period'] = df['Quarter'] + df['Year']


# +
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


# -

df["Period"] = df["Period"].apply(date_time)
df = df.drop(["Year", "Quarter"], axis=1)

df['Local Authority'] = df['Location']

# +
df = df.replace({'Local Authority': {
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

# info needed to create URI's for LA codes
sic = 'http://statistics.data.gov.uk/id/statistical-geography/'
df['Local Authority'] = df['Local Authority'].map(lambda x: 
        sic + x if 'E0' in x else
        sic + x if 'W0' in x else
        sic + x if 'E9' in x else
        sic + x if 'W9' in x
        else x
)

df = df.replace({'Efficiency Rating': {
    "Not recorded": "Not Recorded",
    "not-recorded": 'Not Recorded',
    # "Number of Lodgements": "Grand total"
}})
# -
df['Measure Type'] = 'energy-performance-certificates'
df['Unit'] = 'Count'

# +
# #Codes for creating local codelist
# g = pd.DataFrame()

# g["Label"] = df["Location"]
# g["URI"] = df["Local Authority"]

# g["Parent URI"] = None
# g.index += 1
# g["Sort Priority"] = g.index
# g["Description"] = None
# g["Local Notation"] = g["Label"].map(lambda x:                            
#     x if 'E0' in x else 
#     x if 'W0' in x else 
#     x if 'E9' in x else 
#     x if 'W9' in x 
#     else pathify(x)
# )

# g.to_csv("./local-authority.csv", index=False)

# -

df

df = df.drop_duplicates()

df = df.replace("", "not-available")

df

df = df[['Period', 'Efficiency Rating', 'Local Authority',
         'Measure Type', 'Unit', 'Value']]

df.to_csv('observations.csv', index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')
