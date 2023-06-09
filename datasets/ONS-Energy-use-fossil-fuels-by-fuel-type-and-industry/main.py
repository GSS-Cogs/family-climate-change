#!/usr/bin/env python
# coding: utf-8
import json
import pandas as pandas
from gssutils import *

metadata = Scraper(seed="info.json")
distribution = metadata.distribution(latest = True)

#reterieve the id from info.json for URI's (use later)
with open("info.json", "r") as read_file:
    data = json.load(read_file)
    title_id = data['id']

tabs = distribution.as_databaker()
tabs = tabs[2:]

dataframes = []
for tab in tabs:
    pivot = tab.excel_ref("A1").shift(0, 4)
    remove = tab.filter("Notes").expand(DOWN).expand(RIGHT) | tab.filter("SIC (07) group") | tab.filter("Section")
    year = pivot.shift(3, 0).expand(RIGHT).is_not_blank()
    sicSection = tab.filter("Section").expand(DOWN) - remove | tab.excel_ref('A5').expand(DOWN) - remove.expand(DOWN)
    sicGroup = tab.filter("SIC (07) group").expand(DOWN) - remove | tab.excel_ref('B5').expand(DOWN) - remove.expand(DOWN)
    industry = pivot.shift(2, 0).expand(DOWN).is_not_blank() - remove
    
    if tab.name not in "Aviation fuel":
        
        observations = industry.fill(RIGHT).is_not_blank()
        
        if tab.name == 'Fuel oil':
            fueltype = 'Oil'
        elif tab.name == 'Gas oil':
            fueltype = 'Gas oil including marine oil excluding Derv'
        elif tab.name == 'Other':
            fueltype = 'Other fuel'    
        else:
            fueltype = tab.name
            
        dimensions = [
            HDim(year, 'Year', DIRECTLY, ABOVE),
            HDim(industry, 'Industry', DIRECTLY, LEFT),
            HDim(sicSection, 'SIC Section', DIRECTLY, LEFT),
            HDim(sicGroup, 'SIC Group', DIRECTLY, LEFT),
            HDimConst('Fuel', fueltype)
        ]
        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        # savepreviewhtml(tidy_sheet,fname=tab.name + "Preview.html")
        df = tidy_sheet.topandas()
        df['SIC Group'] = df['SIC Group'].str.rstrip("0")
        df['SIC Group'] = df['SIC Group'].str.rstrip(".")
        dataframes.append(df)

    elif tab.name == "Aviation fuel":
        remove = tab.filter("Notes").expand(DOWN).expand(RIGHT) | tab.filter("SIC (07) group") | tab.filter("Section")
        industry = tab.excel_ref('C6').expand(DOWN) - remove
        fuel = tab.excel_ref('D6').expand(DOWN).is_not_blank() - tab.excel_ref('D25').expand(DOWN).is_not_blank()
        observations = fuel.fill(RIGHT).is_not_blank() - remove
        
        dimensions = [
                HDim(year, 'Year', DIRECTLY, ABOVE),
                HDim(industry, 'Industry', DIRECTLY, LEFT),
                HDim(sicSection, 'SIC Section', DIRECTLY, LEFT),
                HDim(sicGroup, 'SIC Group', DIRECTLY, LEFT),
                HDim(fuel, 'Fuel', DIRECTLY, LEFT)
            ]
        # savepreviewhtml(tidy_sheet,fname=tab.name + "Preview.html")
        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        df = tidy_sheet.topandas()
        df['SIC Group'] = df['SIC Group'].str.rstrip("0")
        df['SIC Group'] = df['SIC Group'].str.rstrip(".")
        # savepreviewhtml(tidy_sheet,fname=tab.name + "Preview.html")
        dataframes.append(df)

df = pd.concat(dataframes)

df.rename(columns = {'DATAMARKER' : 'Marker', 'OBS' : 'Value'}, inplace=True)
df.replace({'Marker' : {'c' : 'confidential'},
                 'Fuel' : {"('DERV',)" : 'DERV'}},  inplace=True)

df['Year'] = df['Year'].astype(float).astype(int)
df['Industry'] = df['Industry'].apply(pathify)
df['SIC Group'] = df['SIC Group'].apply(pathify)

df['SIC Group'] = df.apply(lambda x: x['SIC Section'] if x['SIC Group'] == '' or x['SIC Group'] == '-' else x['SIC Group'], axis=1)
df['SIC Group'] = df.apply(lambda x: x['Industry'] if x['SIC Group'] == '-' and x['SIC Section'] == '-' else x['SIC Group'], axis=1)
df['SIC Group'] = df.apply(lambda x: x['Industry'] if x['SIC Group'] == '' and x['SIC Section'] == '' else x['SIC Group'], axis=1)

# +
#info needed to create URI's for section 
unique = 'http://gss-data.org.uk/data/gss_data/climate-change/' + title_id + '#concept/sic-2007/'
sic = 'http://business.data.gov.uk/companies/def/sic-2007/'

#create the URI's from the section column 
df['SIC Group'] = df['SIC Group'].map(lambda x: unique + x if '-' in x else (unique + x if 'total' in x else sic + x))
df.drop(['SIC Section', 'Industry'], axis = 1,  inplace=True)
# -

df.rename(columns = {'SIC Group' : 'Section', 'Period' : 'Year'},  inplace=True)
df = df[['Year', 'Section','Fuel', 'Value', 'Marker']]

COLUMNS_TO_NOT_PATHIFY = ['Year', 'Section','Fuel', 'Marker', 'Value']
for col in df.columns.values.tolist():
	if col in COLUMNS_TO_NOT_PATHIFY:
		continue
	try:
		df[col] = df[col].apply(pathify)
	except Exception as err:
		raise Exception('Failed to pathify column "{}".'.format(col)) from err

df = df.drop_duplicates()

df.to_csv('observations.csv', index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')

