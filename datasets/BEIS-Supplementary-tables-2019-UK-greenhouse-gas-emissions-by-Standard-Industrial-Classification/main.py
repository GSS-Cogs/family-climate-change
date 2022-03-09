# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.7
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# ## BEIS-Supplementary-tables-2019-UK-greenhouse-gas-emissions-by-Standard-Industrial-Classification

# +
import json
import pandas as pd
from gssutils import *

metadata = Scraper(seed="info.json")
distribution = metadata.distributions[-4] #Could probably change this to check mediatype and name to get distribution 
tabs = distribution.as_databaker()
# -

#reterieve the id from info.json for URI's (use later)
with open("info.json", "r") as read_file:
    data = json.load(read_file)
    title = data['id']

tidied_sheets = []
for tab in tabs:
    tab_list = [tab.name for tab in tabs]
    if tab.name in tab_list[1:-1]:
        emissions_type = tab.excel_ref('A1').is_not_blank()
        section = tab.excel_ref('A4').expand(DOWN) - tab.excel_ref('A27').expand(DOWN)
        section_name = tab.excel_ref('C4').expand(DOWN) - tab.excel_ref('C27').expand(DOWN) 
        year = tab.excel_ref('D3').expand(RIGHT).is_not_blank()
        observations = section_name.fill(RIGHT).is_not_blank()

        dimensions = [
            HDim(section, 'Section breakdown', CLOSEST, UP), # will be dropped 
            HDim(section_name, 'Industry Section Name', DIRECTLY, LEFT), # will be dropped 
            HDim(year, 'Year', DIRECTLY, ABOVE),
            HDim(emissions_type, 'Estimated territorial emissions type', CLOSEST, ABOVE),
        ]
        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        table = tidy_sheet.topandas()
        table['Section'] = table.apply(lambda x: x['Industry Section Name'] if x['Section breakdown'] == '-' else x['Section breakdown'], axis=1)
        tidied_sheets.append(table)
        
        bottom_block = tab.excel_ref('A164').expand(RIGHT).expand(DOWN)
        sic_group = tab.excel_ref('A31').expand(DOWN) - bottom_block
        section = tab.excel_ref('B31').expand(DOWN) - bottom_block 
        group_name = tab.excel_ref('C31').expand(DOWN) - bottom_block
        year = tab.excel_ref('D30').expand(RIGHT).is_not_blank()
        observations = group_name.fill(RIGHT).is_not_blank()

        dimensions2 = [
            HDim(sic_group, 'SIC(07)Group', DIRECTLY, LEFT),
            HDim(section, 'Section breakdown', DIRECTLY, LEFT), # will be dropped
            HDim(group_name, 'Industy Group Name', DIRECTLY, LEFT), # will be dropped 
            HDim(year, 'Year', DIRECTLY, ABOVE),
            HDim(emissions_type, 'Estimated territorial emissions type', CLOSEST, ABOVE),
        ]
        tidy_sheet = ConversionSegment(tab, dimensions2, observations)
        table = tidy_sheet.topandas()
        table['Section'] = table.apply(lambda x: x['Industy Group Name'] if x['SIC(07)Group'] == '-' else x['SIC(07)Group'], axis=1)
        table['Section'] = table['Section'].str.rstrip("0")
        table['Section'] = table['Section'].str.rstrip(".")
        table['Section'] = table['Section'].apply(lambda x: '{0:0>2}'.format(x))
        table['Section'] = table['Section'].apply(pathify)
        tidied_sheets.append(table)
    
    elif tab.name == '8.9':   
        emissions_type = tab.excel_ref('A1').is_not_blank()
        section = tab.excel_ref('A4').expand(DOWN).is_not_blank() - tab.excel_ref('A403').expand(DOWN)
        sic_group = tab.excel_ref('B4').expand(DOWN).is_not_blank() - tab.excel_ref('B403').expand(DOWN)
        group_name = tab.excel_ref('C4').expand(DOWN).is_not_blank() - tab.excel_ref('C403').expand(DOWN) 
        ncs = tab.excel_ref('D4').expand(DOWN) - tab.excel_ref('D403').expand(DOWN) 
        year = tab.excel_ref('E3').expand(RIGHT).is_not_blank()
        observations = ncs.fill(RIGHT).is_not_blank()
    
        dimensions = [
            HDim(section, 'Section breakdown', CLOSEST,ABOVE), # will be dropped 
            HDim(sic_group, 'SIC(07)Group', CLOSEST,ABOVE),  # will be dropped 
            HDim(group_name, 'Industy Group Name', CLOSEST,ABOVE), # will be dropped 
            HDim(ncs, 'National Communication Sector', DIRECTLY, LEFT),
            HDim(year, 'Year', DIRECTLY, ABOVE),
            HDim(emissions_type, 'Estimated territorial emissions type', CLOSEST, ABOVE),
        ]
        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        table = tidy_sheet.topandas()
        table['Section'] = table.apply(lambda x: x['Industy Group Name'] if x['SIC(07)Group'] == '-' else x['SIC(07)Group'], axis=1)
        table['Section'] = table['Section'].str.rstrip("0")
        table['Section'] = table['Section'].str.rstrip(".")
        table['Section'] = table['Section'].apply(lambda x: '{0:0>2}'.format(x))
        table['Section'] = table['Section'].apply(pathify)
        tidied_sheets.append(table)
    else :
        continue

# +
df = pd.concat(tidied_sheets, sort=True).fillna('Not applicable')
df.rename(columns={'OBS' : 'Value', 'DATAMARKER' : 'Marker'}, inplace=True)
#Post Processing (Spliting the cell A1 to represent the Emissions type of each tab)
start = ' territorial '
end = ' by'
df['Estimated territorial emissions type'] = df['Estimated territorial emissions type'].str.split(start).str[1].str.split(end).str[0]

df['Year'] = df['Year'].str.replace('\.0', '')
#df['Year'] = 'year/' + df['Year']
df['Value'] = df['Value'].astype(str).astype(float).round(1)
df = df.replace({'Section' : {'Consumer expenditure' : 'consumer-expenditure' , 
                              'Land use, land use change and forestry (LULUCF)' : 'land-use-land-use-change-and-forestry-lulucf'}})

#
#info needed to create URI's for section 
unique = 'http://gss-data.org.uk/data/gss_data/climate-change/' + title + '#concept/sic-2007/'
sic = 'http://business.data.gov.uk/companies/def/sic-2007/'
#create the URI's from the section column 
df['Section'] = df['Section'].map(lambda x: unique + x if '-' in x else sic + x)
#only need the following columns
df = df[['Year', 'Estimated territorial emissions type','Section', 'National Communication Sector', 'Value']]

for col in ['Estimated territorial emissions type', 'National Communication Sector']:
    df[col] = df[col].apply(pathify)

df = df.drop_duplicates().replace({'National Communication Sector' : {'lulucf' : 'land-use-land-use-change-and-forestry'}})

# -


df.to_csv('observations.csv', index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')
