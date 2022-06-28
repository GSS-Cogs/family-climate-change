# ## ONS-Atmospheric-emissions-greenhouse-gases-by-industry-and-gas-1990-2020
import json
import pandas as pandas
from gssutils import *
info = json.load(open('info.json'))
metadata = Scraper(seed="info.json")
metadata.dataset.title = info['title']
distribution = metadata.distribution(
    mediaType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", latest=True)

# +
# reterieve the id from info.json for URI's (use later)
title_id = info['id']

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
    elif 'GHG total' in tab.name:
        remove_bottom_section = tab.excel_ref('A26').expand(DOWN).expand(RIGHT)

        year = tab.excel_ref('D4').expand(RIGHT).is_not_blank()
        section = tab.excel_ref('A5').expand(DOWN) - remove_bottom_section
        section_name = tab.excel_ref('C5').expand(DOWN) - remove_bottom_section
        observations = year.fill(DOWN).is_not_blank() - remove_bottom_section
        measure_type = tab.excel_ref('AH3')

        dimensions = [
            HDim(section, 'Section breakdown', DIRECTLY, LEFT),  # will be dropped
            HDim(section_name, 'Industry Section Name',
                DIRECTLY, LEFT),  # will be dropped
            HDim(year, 'Year', DIRECTLY, ABOVE),
            HDimConst('Emission Type', tab.name),
            HDim(measure_type, 'Measure Type', CLOSEST, ABOVE),
        ]
        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        #savepreviewhtml(tidy_sheet, fname = tab.name+ "Preview.html")
        table = tidy_sheet.topandas()
        table['Section'] = table.apply(lambda x: x['Industry Section Name'] if x['Section breakdown'] == '-'
                                    else x['Section breakdown'], axis=1)
        table['Section'] = table['Section'].apply(pathify_section_values)
        tidied_sheets.append(table)

    else:
        remove_bottom_section = tab.excel_ref('A26').expand(DOWN).expand(RIGHT)

        year = tab.excel_ref('D4').expand(RIGHT).is_not_blank()
        section = tab.excel_ref('A5').expand(DOWN) - remove_bottom_section
        section_name = tab.excel_ref('C5').expand(DOWN) - remove_bottom_section
        observations = year.fill(DOWN).is_not_blank() - remove_bottom_section
        measure_type = tab.excel_ref('AH3')

        dimensions = [
            HDim(section, 'Section breakdown', DIRECTLY, LEFT),  # will be dropped
            HDim(section_name, 'Industry Section Name',
                DIRECTLY, LEFT),  # will be dropped
            HDim(year, 'Year', DIRECTLY, ABOVE),
            HDimConst('Emission Type', tab.name),
            HDim(measure_type, 'Measure Type', CLOSEST, ABOVE),
        ]
        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        #savepreviewhtml(tidy_sheet, fname = tab.name+ "Preview.html")
        table = tidy_sheet.topandas()
        table['Section'] = table.apply(lambda x: x['Industry Section Name'] if x['Section breakdown'] == '-'
                                    else x['Section breakdown'], axis=1)
        table['Section'] = table['Section'].apply(pathify_section_values)
        tidied_sheets.append(table)

        # Bottom part

        # remove_top_section = tab.excel_ref('A27').expand(UP).expand(RIGHT)
        remove_notes = tab.excel_ref('A162').expand(DOWN).expand(RIGHT)

        sic_group = tab.excel_ref('A31').expand(DOWN) - remove_notes
        section = tab.excel_ref('B31').expand(DOWN) - remove_notes
        section_name = tab.excel_ref('C31').expand(DOWN) - remove_notes
        observations = section_name.fill(RIGHT).is_not_blank()

        dimensions = [
            HDim(sic_group, 'SIC(07)Group', DIRECTLY, LEFT),
            HDim(section, 'Section breakdown', DIRECTLY, LEFT),  # will be dropped
            HDim(section_name, 'Industry Section Name',
                DIRECTLY, LEFT),  # will be dropped
            HDim(year, 'Year', DIRECTLY, ABOVE),
            HDim(measure_type, 'Measure Type', CLOSEST, ABOVE),
            HDimConst('Emission Type', tab.name),
        ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        #savepreviewhtml(tidy_sheet, fname = tab.name+ "Preview.html")
        table = tidy_sheet.topandas()
        table['Section'] = table.apply(lambda x: x['Industy Section Name'] if x['SIC(07)Group'] == '-'
                                    else x['SIC(07)Group'], axis=1)

        table['Section'] = table['Section'].str.rstrip("0")
        table['Section'] = table['Section'].str.rstrip(".")
        table['Section'] = table['Section'].apply(lambda x: '{0:0>2}'.format(x))
        table['Section'] = table['Section'].apply(pathify_section_values)
        table['Section'] = table['Section'].apply(pathify)
        tidied_sheets.append(table)

df = pd.concat(tidied_sheets, sort=True)
df.rename(columns={'OBS': 'Value', 'DATAMARKER': 'Marker'}, inplace=True)
df = df.replace(
    {'Section': {'Total': 'total', 'Consumer expenditure': 'consumer-expenditure'}})
df['Year'] = df['Year'].astype(str).replace('\.0', '', regex=True)
# +
# info needed to create URI's for section
unique = 'http://gss-data.org.uk/data/gss_data/climate-change/' + \
    title_id + '#concept/sic-2007/'
sic = 'http://business.data.gov.uk/companies/def/sic-2007/'
# create the URI's from the section column
df['Section'] = df['Section'].map(
    lambda x: unique + x if '-' in x else (unique + x if 'total' in x else sic + x))

# df['Emission Type'] = df['Emission Type'].apply(pathify)
# df = df.replace({'Emission Type': {'total-ghg': 'ghg-total'}})
df['Measure Type'] = df['Measure Type'].str.strip()
df['Measure Type'] = df['Measure Type'].map(
    lambda x: 'Mass of air emissions of carbon dioxide equivalent' if 'carbon dioxide' in x else 'Mass of air emissions')
# df['Measure Type'] = df['Measure Type'].apply(pathify)

# only need the following columns
df = df[['Year', 'Section', 'Emission Type', 'Measure Type', 'Value']]
# -
df = df.drop_duplicates()
df.to_csv('observations.csv', index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')
