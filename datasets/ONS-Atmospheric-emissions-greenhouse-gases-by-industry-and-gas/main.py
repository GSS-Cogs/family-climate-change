# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.5
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# +
import json
import pandas as pandas
from gssutils import *

cubes = Cubes('info.json')
info = json.load(open('info.json'))
landingPage = info['landingPage']
metadata = Scraper(seed="info.json")
distribution = metadata.distribution(latest = True)
title = distribution.title

# +
#reterieve the id from info.json for URI's (use later)
with open("info.json", "r") as read_file:
    data = json.load(read_file)
    title_id = data['id']

def pathify_section_values(section):
    if 'Total' in section:
        section = pathify(section)
        return section
    if 'Travel' in section or 'travel' in section:
        section = pathify(section)
        return section
    else: 
        return section


# -

tabs = distribution.as_databaker()
tidied_sheets = []
for tab in tabs:
    if 'Contents' in tab.name:
        continue
    remove_bottom_section = tab.excel_ref('A31').expand(DOWN).expand(RIGHT)
    year = tab.excel_ref('C4').expand(RIGHT).is_not_blank()
    section = tab.excel_ref('A4').expand(DOWN)
    section_name = tab.excel_ref('C4').expand(DOWN)
    observations = year.fill(DOWN).is_not_blank() - remove_bottom_section
    measure_type = tab.excel_ref('AH3')

    #Top part (includes 2020 provisional data for total ghg)
    dimensions = [
        HDim(section, 'Section breakdown', DIRECTLY, LEFT), # will be dropped 
        HDim(section_name, 'Industry Section Name', DIRECTLY, LEFT), # will be dropped 
        HDim(year, 'Year', DIRECTLY, ABOVE),
        HDimConst('Emission Type', tab.name),
        HDim(measure_type, 'Measure Type', CLOSEST, ABOVE),
        ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    #savepreviewhtml(tidy_sheet, fname = tab.name+ "Preview.html")
    table = tidy_sheet.topandas()
    table['Section'] = table.apply(lambda x: x['Industry Section Name'] if x['Section breakdown'] == '-' 
                                   else (x['Industry Section Name'] if x['Section breakdown'] == '' 
                                         else x['Section breakdown']), axis=1)
    table['Section'] = table['Section'].apply(pathify_section_values)
    tidied_sheets.append(table)
    
    #Bottom part 
    section_name = tab.excel_ref('C31').expand(DOWN)
    remove_top_section = tab.excel_ref('A31').expand(UP).expand(RIGHT)
    remove_notes = tab.excel_ref('A165').expand(DOWN).expand(RIGHT)
    sic_group = tab.excel_ref('A31').expand(DOWN) - remove_notes
    section = tab.excel_ref('B31').expand(DOWN) - remove_notes
    observations = year.fill(DOWN).is_not_blank() - remove_top_section - remove_notes
    
    dimensions = [
        HDim(sic_group, 'SIC(07)Group', DIRECTLY, LEFT),
        HDim(section, 'Section breakdown', DIRECTLY, LEFT), # will be dropped 
        HDim(section_name, 'Industry Section Name', DIRECTLY, LEFT), # will be dropped 
        HDim(year, 'Year', DIRECTLY, ABOVE),
        HDim(measure_type, 'Measure Type', CLOSEST, ABOVE),
        HDimConst('Emission Type', tab.name),
        ]
    
    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    #savepreviewhtml(tidy_sheet, fname = tab.name+ "Preview.html")
    table = tidy_sheet.topandas()
    table['Section'] = table.apply(lambda x: x['Industy Section Name'] if x['SIC(07)Group'] == '-' 
                                   else (x['Industry Section Name'] if x['SIC(07)Group'] == '' 
                                       else x['SIC(07)Group']), axis=1)
    
    table['Section'] = table['Section'].str.rstrip("0")
    table['Section'] = table['Section'].str.rstrip(".")
    table['Section'] = table['Section'].apply(lambda x: '{0:0>2}'.format(x))
    table['Section'] = table['Section'].apply(pathify_section_values)
    table['Section'] = table['Section'].apply(pathify)
    tidied_sheets.append(table)    

# +
df = pd.concat(tidied_sheets, sort=True)
df.rename(columns={'OBS' : 'Value', 'DATAMARKER' : 'Marker'}, inplace=True)
df = df.replace({'Section' : {'Total' : 'total', 'Consumer expenditure' : 'consumer-expenditure'}})
df['Year'] = df['Year'].astype(str).replace('\.0', '', regex=True)

#info needed to create URI's for section 
unique = 'http://gss-data.org.uk/data/gss_data/climate-change/' + title_id + '#concept/sic-2007/'
sic = 'http://business.data.gov.uk/companies/def/sic-2007/'
#create the URI's from the section column 
df['Section'] = df['Section'].map(lambda x: unique + x if '-' in x else (unique + x if 'total' in x else sic + x))

df['Emission Type'] = df['Emission Type'].apply(pathify)
df['Measure Type'] = df['Measure Type'].str.strip()
df['Measure Type'] = df['Measure Type'].map(lambda x: 'Mass of air emissions of carbon dioxide equivalent'  if 'carbon dioxide' in x else 'Mass of air emissions')
df['Measure Type'] = df['Measure Type'].apply(pathify)
df['Units'] = 'thousand-tonnes'
#only need the following columns
df = df[['Year','Section','Emission Type', 'Value', 'Measure Type', 'Units']]
# -

cubes.add_cube(metadata, df.drop_duplicates(), metadata.dataset.title)
cubes.output_all()
