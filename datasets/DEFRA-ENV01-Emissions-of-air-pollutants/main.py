# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.10.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# DEFRA-ENVO1-Emmissions of air pollutants

import json
import pandas as pd
from gssutils import *

cubes = Cubes('info.json')

info = json.load(open('info.json'))
landingPage = info['landingPage']
landingPage

metadata = Scraper(seed='info.json')

distribution = metadata.distribution(latest=True)

tabs = distribution.as_databaker()
print(len(tabs), ' ', [tab.name for tab in tabs])

contents = tabs[1]
titles = contents.excel_ref('B9').expand(DOWN) - contents.excel_ref('B22').expand(DOWN)
title_list = [title.value for title in titles]
print(*title_list, sep ='\n')
print(len(title_list))

trace = TransformTrace()

i = 0
for tab in tabs:
    if any(character in tab.name for character in '1234'):
        title = title_list[i]
        print(tab.name, ' ', title)
        metadata.dataset.title = title
        columns = ['Sector', 'Period', 'Measure Type', 'Value', 'Total Value', 'Unit']
        trace.start(title, tab, columns, distribution.downloadURL) 
        
        bottom_block = tab.excel_ref('A').filter('NATIONAL TOTAL').shift(DOWN).expand(RIGHT).expand(DOWN)
        measures = tab.excel_ref('C').filter("Emissions ('000 tonnes)").expand(RIGHT).is_not_blank()
        year = measures.shift(0, -2)
        sector = tab.excel_ref('C').filter("Emissions ('000 tonnes)").shift(-2,0).fill(DOWN).is_not_blank() - bottom_block
        observations = sector.shift(RIGHT).fill(RIGHT).is_not_blank()
        
        dimensions = [
                    HDim(year, 'Period', 'DIRECTLY', ABOVE),
                    HDim(sector, 'Sector', 'DIRECTLY', LEFT),
                    HDimConst('Measure Type', 'emissions'),
                    HDimConst('Unit', "tonnes")
                ]
        
        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        table = tidy_sheet.topandas()
        table['OBS'] = table['OBS']*1000
        trace.store('dataframe' + tab.name  + str(i), table)

        df = trace.combine_and_trace(title, 'dataframe' + tab.name  + str(i)).fillna('')
        df['Period'] = df['Period'].str.replace('\.0', '')
        df.rename(columns={'OBS':'Value'}, inplace=True)
        df['Value'] = pd.to_numeric(df['Value'], downcast='float')
        df['Value'] = df['Value'].astype(float).round().astype(int)

        df['Total Value'] = ' ' 
        df.loc[(df['Sector'] == 'NATIONAL TOTAL'), 'Total Value'] = df.loc[(df['Sector'] == 'NATIONAL TOTAL'), 'Value']
        df.loc[(df['Sector'] == 'NATIONAL TOTAL'), 'Value'] = ' '
        df.loc[(df['Sector'] == 'NATIONAL TOTAL'), 'Sector'] = 'All'
        df = df[['Sector', 'Period', 'Measure Type', 'Value', 'Total Value', 'Unit']]

        cubes.add_cube(metadata, df,  metadata.dataset.title)
        i += 2


    elif tab.name == 'Table5':
        title = title_list[i]
        print(tab.name, ' ', title)
        metadata.dataset.title = title
        columns = ['Sector', 'Period', 'Measure Type', 'Value', 'Total Value', 'Unit']

        trace.start(title, tab, columns, distribution.downloadURL)

        bottom_block = tab.excel_ref('C').filter('Source: Rothamsted Research').expand(RIGHT).expand(DOWN)
        measures = tab.excel_ref('C').filter("Emissions ('000 tonnes)").expand(RIGHT).is_not_blank()
        year = measures.shift(0, -2)
        sector = tab.excel_ref('C').filter("Emissions ('000 tonnes)").shift(-2,0).fill(DOWN).is_not_blank() - bottom_block
        
        observations = sector.shift(RIGHT).fill(RIGHT).is_not_blank()
        
        dimensions = [
                    HDim(year, 'Period', 'DIRECTLY', ABOVE),
                    HDim(sector, 'Source', 'DIRECTLY', LEFT),
                    HDimConst('Measure Type', 'emissions'),
                    HDimConst('Unit', "tonnes")
                ]
        
        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        table = tidy_sheet.topandas()
        table['OBS'] = table['OBS']*1000
        trace.store('dataframe' + tab.name  + str(i), table)

        df = trace.combine_and_trace(title, 'dataframe' + tab.name  + str(i)).fillna('')
        df['Period'] = df['Period'].str.replace('\.0', '')
        df.rename(columns={'OBS':'Value'}, inplace=True)
        df['Value'] = pd.to_numeric(df['Value'], downcast='float')
        df['Value'] = df['Value'].astype(float).round().astype(int)

        df['Total Value'] = ' ' 
        df.loc[(df['Source'] == 'Total Emissions from Agriculture'), 'Total Value'] = df.loc[(df['Source'] == 'Total Emissions from Agriculture'), 'Value']
        df.loc[(df['Source'] == 'Total Emissions from Agriculture'), 'Value'] = ' '
        df.loc[(df['Source'] == 'Total Emissions from Agriculture'), 'Source'] = 'All'
        df = df[['Source', 'Period', 'Measure Type', 'Value', 'Total Value', 'Unit']]
            
        cubes.add_cube(metadata, df, metadata.dataset.title)
        if i == 8:
            i = i
        

        j = i + 1  
    elif any(character in tab.name for character in '67'):
        title = title_list[j]
        print(tab.name, ' ', title)
        metadata.dataset.title = title
        columns = ['Sector', 'Period', 'Measure Type', 'Value', 'Total Value', 'Unit']

        trace.start(title, tab, columns, distribution.downloadURL)
        if tab.name == 'Table6a&6b':
            bottom_block = tab.excel_ref('A').filter('Memo Items1').expand(DOWN)
        elif tab.name == 'Table7a&7b':
            bottom_block = tab.excel_ref('A').filter('Memo Items2').expand(DOWN)
        measures = tab.excel_ref('C').filter("Emissions ('000 tonnes)").expand(RIGHT).is_not_blank()
        year =  measures.shift(UP).shift(UP)
        sector = tab.excel_ref('C').filter("Emissions ('000 tonnes)").shift(-2,0).fill(DOWN).is_not_blank() - bottom_block
        total = tab.excel_ref('A').filter('NATIONAL TOTAL').expand(RIGHT).is_not_blank()
        observations = sector.shift(RIGHT).fill(RIGHT).is_not_blank()
        
        dimensions = [
                    HDim(sector, 'Sector', 'DIRECTLY', LEFT),
                    HDim(year, 'Period', 'DIRECTLY', ABOVE),
                    HDimConst('Measure Type', 'emissions'),
                    HDimConst('Unit', "tonnes")
                ]
        
        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        table = tidy_sheet.topandas()
        table['OBS'] = table['OBS']*1000
        trace.store('dataframe' + tab.name + str(j), table)
        
        df_67 = trace.combine_and_trace(title, 'dataframe' + tab.name + str(j)).fillna('')
        df_67['Period'] = df_67['Period'].str.replace('\.0', '')
        df_67.rename(columns={'OBS':'Value'}, inplace=True)
        df_67['Value'] = df_67['Value'].fillna('-1')
        df_67['Value'] = pd.to_numeric(df_67['Value'], downcast='float')

        df_67['Value'] = (df_67['Value'].fillna(0).astype(float).round().astype(int).astype(object).where(df_67['Value'].notnull()))
       
        df_67['Total Value'] = ' ' 
        df_67.loc[(df_67['Sector'] == 'NATIONAL TOTAL'), 'Total Value'] = df_67.loc[(df_67['Sector'] == 'NATIONAL TOTAL'), 'Value']
        df_67.loc[(df_67['Sector'] == 'NATIONAL TOTAL'), 'Value'] = ' '
        df_67.loc[(df_67['Sector'] == 'NATIONAL TOTAL'), 'Sector'] = 'All'
        df_67 = df_67[['Sector', 'Period', 'Measure Type', 'Value', 'Total Value', 'Unit']]
        j += 1
        cubes.add_cube(metadata, df_67, metadata.dataset.title)


        title2 = title_list[j]
        metadata.dataset.title = title2
        print(tab.name, ' ', title2)
        columns2 = ['Sector', 'Period', 'Measure Type', 'Value']
        trace.start(title2, tab, columns2, distribution.downloadURL)
        measures = tab.excel_ref('C').filter("% of total emissions").expand(RIGHT).is_not_blank()
        year2 = measures.shift(UP).shift(UP)
        sector2 = tab.excel_ref('C').filter('% of total emissions').shift(-2,0).fill(DOWN).is_not_blank()
        observations2 = sector2.shift(RIGHT).fill(RIGHT).is_not_blank()
        
        dimensions2 = [
                    HDim(sector2, 'Sector', 'DIRECTLY', LEFT),
                    HDim(year2, 'Period', 'DIRECTLY', ABOVE),
                    HDimConst('Measure Type', "% of total emissions")
            ]
        tidi_sheet_2 = ConversionSegment(tab, dimensions2, observations2)
        table2 = tidi_sheet_2.topandas()
        trace.store('dataframe' + tab.name + str(j), table2)
        df_percent = trace.combine_and_trace(title2, 'dataframe' + tab.name + str(j)).fillna('')
        df_percent['Period'] = df_percent['Period'].str.replace('\.0', '')
        df_percent.rename(columns={'OBS':'Value'}, inplace=True)
        df_percent['Value'] = pd.to_numeric(df_percent['Value'], downcast='float')
        df_percent['Value'] = df_percent['Value'].round(2)
        df_percent = df_percent[['Sector', 'Period', 'Measure Type', 'Value']]
        j += 1
        cubes.add_cube(metadata, df_percent, metadata.dataset.title)

cubes.output_all()
