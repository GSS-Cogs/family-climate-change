# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.3
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

cubes = Cubes("info.json")
info = json.load(open("info.json"))
landingPage = info["landingPage"]
metadata = Scraper(seed="info.json")
distribution = metadata.distributions[-4] #Could probably change this to check mediatype and name to get distribution 
tabs = distribution.as_databaker()
# -

distribution

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
            HDim(section, 'Section', CLOSEST, UP),
            HDim(section_name, 'Industry Section Name', DIRECTLY, LEFT),
            HDim(year, 'Year', DIRECTLY, ABOVE),
            HDim(emissions_type, 'Estimated territorial emissions type', CLOSEST, ABOVE),
        ]
        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        table = tidy_sheet.topandas()
        tidied_sheets.append(table)
        
        bottom_block = tab.excel_ref('A164').expand(RIGHT).expand(DOWN)
        sic_group = tab.excel_ref('A31').expand(DOWN) - bottom_block
        section = tab.excel_ref('B31').expand(DOWN) - bottom_block 
        group_name = tab.excel_ref('C31').expand(DOWN) - bottom_block
        year = tab.excel_ref('D30').expand(RIGHT).is_not_blank()
        observations = group_name.fill(RIGHT).is_not_blank()

        dimensions2 = [
            HDim(sic_group, 'SIC(07)Group', CLOSEST, UP),
            HDim(section, 'Section', CLOSEST, UP),
            HDim(group_name, 'Industy Group Name', DIRECTLY, LEFT),
            HDim(year, 'Year', DIRECTLY, ABOVE),
            HDim(emissions_type, 'Estimated territorial emissions type', CLOSEST, ABOVE),
        ]
        tidy_sheet = ConversionSegment(tab, dimensions2, observations)
        table = tidy_sheet.topandas()
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
            HDim(section, 'Section', CLOSEST,ABOVE),
            HDim(sic_group, 'SIC(07)Group', CLOSEST,ABOVE), 
            HDim(group_name, 'Industy Group Name', CLOSEST,ABOVE),
            HDim(ncs, 'National Communication Sector', DIRECTLY, LEFT),
            HDim(year, 'Year', DIRECTLY, ABOVE),
            HDim(emissions_type, 'Estimated territorial emissions type', CLOSEST, ABOVE),
        ]
        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        #savepreviewhtml(tidy_sheet, fname=tab.name + "Preview.html")
        table = tidy_sheet.topandas()
        tidied_sheets.append(table)
    else: 
        continue

# +
df = pd.concat(tidied_sheets, sort=True).fillna('Not applicable')
df.rename(columns={'OBS' : 'Value', 'DATAMARKER' : 'Marker'}, inplace=True)
#Post Processing (Spliting the cell A1 to represent the Emissions type of each tab)
start = ' territorial '
end = ' by'
df['Estimated territorial emissions type'] = df['Estimated territorial emissions type'].str.split(start).str[1].str.split(end).str[0]

df['Year'] = df['Year'].str.replace('\.0', '')
df['Year'] = 'year/' + df['Year']
df['Value'] = df['Value'].astype(str).astype(float).round(1)
df = df[['Year', 'Estimated territorial emissions type', 'National Communication Sector', 'SIC(07)Group', 'Section', 'Industry Section Name', 'Industy Group Name', 'Value']]
for col in ['Estimated territorial emissions type', 'National Communication Sector', 'Section', 'Industry Section Name', 'Industy Group Name']:
    df[col] = df[col].apply(pathify)

# - symbol inside section (No explination given in source data to explain meaning. Setting as Unknown.)
df['Section'] = df['Section'].str.replace('-', 'Unknown')

del df['SIC(07)Group']

cubes.add_cube(metadata, df, metadata.dataset.title)

cubes.output_all()
df

# +
# Commenting out for now - for SIC code - move above 

#title = 'final-uk-greenhouse-gas-emissions-national-statistics'
#unique = 'http://gss-data.org.uk/data/gss_data/climate-change/' + title + '#concept/sic-2007/'
#sic = 'http://business.data.gov.uk/companies/def/sic-2007/'

#df['SIC(07)Group'] = df['SIC(07)Group'].str.replace('\.0', '')
#df = df.replace({'SIC(07)Group' : {'Not applicable' : 'not-applicable' , '-' : 'unknown', '117' : '11.07', '111-06' : '11.01-06'}})

#df['SIC(07)Group'] = df['SIC(07)Group'].str.replace(' ', '')
#df['SIC(07)Group'] = df['SIC(07)Group'].apply(lambda x: '{0:0>2}'.format(x))
#df['SIC(07)Group'] = df['SIC(07)Group'].map(lambda x: unique + x if '-' in x 
#                                            else( unique + x if '+' in x 
#                                                 else ( unique + x if '/' in x 
#                                                       else (unique + x if 'unknown' in x else sic + x))))

