# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.4
#   kernelspec:
#     display_name: Python 3.8.8 64-bit
#     name: python3
# ---

# ## DEFRA-ENVO1-Emmissions of air pollutants

import json
import pandas as pd
from gssutils import *

cubes = Cubes('info.json')

info = json.load(open('info.json'))
landingPage = info['landingPage']

metadata = Scraper(seed='info.json')

distribution = metadata.distribution(latest=True)

tabs = distribution.as_databaker()

trace = TransformTrace()

# +
title = 'Emissions of air pollutants in the UK, 1990 to 2019, by pollutant and by major emissions source'
metadata.dataset.title = title
for tab in tabs:
    if any(character in tab.name for character in '123467'):
       
        columns = ['Sector', 'Period', 'Measure Type', 'Value', 'Total Value', 'Unit', 'Pollutant']
        trace.start(title, tab, columns, distribution.downloadURL) 

        bottom_block = tab.excel_ref('A').filter('NATIONAL TOTAL').shift(DOWN).expand(RIGHT).expand(DOWN)
        measures = tab.excel_ref('C').filter("Emissions ('000 tonnes)").expand(RIGHT).is_not_blank()
        year =  measures.shift(UP).shift(UP)
        sector = tab.excel_ref('C').filter("Emissions ('000 tonnes)").shift(-2,0).fill(DOWN).is_not_blank() - bottom_block
        observations = sector.shift(RIGHT).fill(RIGHT).is_not_blank()
        
        if tab.name == 'Table1a&1b':
            pollutant = 'PM10'
        elif tab.name == 'Table2a&2b':
            pollutant = 'PM2.5'
        elif tab.name == 'Table3a&3b':
            pollutant = 'nitrogen oxides'
        elif tab.name == 'Table4a&4b':
            pollutant = 'ammonia'
        elif tab.name == 'Table6a&6b':
            pollutant = 'non-methane volatile organic compounds'
        elif tab.name == 'Table7a&7b':
            pollutant = 'sulphur dioxide'

        dimensions = [
                    HDim(year, 'Period', DIRECTLY, ABOVE),
                    HDim(sector, 'Sector', DIRECTLY, LEFT),
                    HDimConst('Measure Type', 'emissions'),
                    HDimConst('Unit', "tonnes"),
                    HDimConst('Pollutant', pollutant)
                ]
        
        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        table = tidy_sheet.topandas()
        table['OBS'] = table['OBS']*1000
        
        table['Period'] = table['Period'].str.replace('\.0', '')
        table.rename(columns={'OBS':'Value'}, inplace=True)
        table['Value'] = pd.to_numeric(table['Value'], downcast='float')
        table['Value'] = table['Value'].astype(str).astype(float).round(1)
       
        table['Total Value'] = '' 
        table.loc[(table['Sector'] == 'NATIONAL TOTAL'), 'Total Value'] = table.loc[(table['Sector'] == 'NATIONAL TOTAL'), 'Value']
        table.loc[(table['Sector'] == 'NATIONAL TOTAL'), 'Value'] = ''
        table.loc[(table['Sector'] == 'NATIONAL TOTAL'), 'Sector'] = 'All'
        
        trace.store('dataframe', table)

    elif tab.name == 'Table5':
        metadata.dataset.title = title
        columns = ['Sector', 'Period', 'Measure Type', 'Value', 'Total Value', 'Unit', 'Pollutant']

        trace.start(title, tab, columns, distribution.downloadURL)

        bottom_block = tab.excel_ref('C').filter('Source: Rothamsted Research').expand(RIGHT).expand(DOWN)
        measures = tab.excel_ref('C').filter("Emissions ('000 tonnes)").expand(RIGHT).is_not_blank()
        year = measures.shift(0, -2)
        sector = tab.excel_ref('C').filter("Emissions ('000 tonnes)").shift(-2,0).fill(DOWN).is_not_blank() - bottom_block
        pollutant = 'ammonia from agricultural sector'
        
        observations = sector.shift(RIGHT).fill(RIGHT).is_not_blank()
        
        dimensions = [
                    HDim(year, 'Period', DIRECTLY, ABOVE),
                    HDim(sector, 'Source', DIRECTLY, LEFT),
                    HDimConst('Measure Type', 'emissions'),
                    HDimConst('Unit', "tonnes"),
                    HDimConst('Pollutant', pollutant)
                ]
        
        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        table = tidy_sheet.topandas()
        table['OBS'] = table['OBS']*1000

        table['Period'] = table['Period'].str.replace('\.0', '')
        table.rename(columns={'OBS':'Value'}, inplace=True)
        table['Value'] = pd.to_numeric(table['Value'], downcast='float')
        table['Value'] = table['Value'].astype(str).astype(float).round(1)
       
        table['Total Value'] = '' 
        table.loc[(table['Source'] == 'Total Emissions from Agriculture'), 'Total Value'] = table.loc[(table['Source'] == 'Total Emissions from Agriculture'), 'Value']
        table.loc[(table['Source'] == 'Total Emissions from Agriculture'), 'Value'] = ''
        table.loc[(table['Source'] == 'Total Emissions from Agriculture'), 'Source'] = 'All'
        
        trace.store('dataframe', table)
       
df = trace.combine_and_trace(title, 'dataframe').fillna('')

for col in ['Sector', 'Source', 'Measure Type', 'Unit', 'Pollutant']:
    df[col] = df[col].apply(pathify)
df = df.replace('', 'not-applicable')

df = df[['Sector', 'Source', 'Period', 'Measure Type', 'Unit', 'Value', 'Total Value', 'Pollutant']]
cubes.add_cube(metadata, df.drop_duplicates(), metadata.dataset.title) 

# Emissions of air pollutants by emissions source as proportion of total emissions: 1990 to 2019 
title2 = 'Emissions of air pollutants by emissions source as proportion of total emissions: 1990 to 2019'
metadata.dataset.title = title2  
for tab in tabs:   
    if any(character in tab.name for character in '67'):
        columns = ['Sector', 'Period', 'Measure Type', 'Value', 'Total Value', 'Unit']
        
        trace.start(title, tab, columns, distribution.downloadURL)
    
        columns2 = ['Sector', 'Period', 'Measure Type', 'Value', 'Pollutant']
        trace.start(title2, tab, columns2, distribution.downloadURL)
        measures = tab.excel_ref('C').filter("% of total emissions").expand(RIGHT).is_not_blank()
        year2 = measures.shift(UP).shift(UP)
        sector2 = tab.excel_ref('C').filter('% of total emissions').shift(-2,0).fill(DOWN).is_not_blank()
        observations2 = sector2.shift(RIGHT).fill(RIGHT).is_not_blank()

        if tab.name == 'Table6a&6b':
            pollutant = 'non-methane volatile organic compounds'
        elif tab.name == 'Table7a&7b':
            pollutant = 'sulphur dioxide'
        
        dimensions2 = [
                    HDim(sector2, 'Sector', DIRECTLY, LEFT),
                    HDim(year2, 'Period', DIRECTLY, ABOVE),
                    HDimConst('Measure Type', '% of total emissions'),
                    HDimConst('Pollutant', pollutant)
            ]
        tidi_sheet2 = ConversionSegment(tab, dimensions2, observations2)
        table2 = tidi_sheet2.topandas()
        trace.store('dataframe67', table2)
df2 = trace.combine_and_trace(title2, 'dataframe67').fillna('')

df2['Period'] = df2['Period'].str.replace('\.0', '')
df2.rename(columns={'OBS':'Value'}, inplace=True)

df2['Value'] = pd.to_numeric(df2['Value'], downcast='float')
df2['Value'] = df2['Value'].fillna(0)
df2['Value'] = df2['Value'].astype(str).astype(float).round(1)

for col in ['Sector', 'Pollutant']:
    df2[col] = df2[col].apply(pathify)
    
df2 = df2.replace('', 'not-applicable')
df2 = df2[['Sector', 'Period', 'Measure Type', 'Value', 'Pollutant']]

cubes.add_cube(metadata, df2.drop_duplicates(), metadata.dataset.title)
# -

cubes.output_all()
