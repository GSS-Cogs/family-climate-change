#!/usr/bin/env python
# coding: utf-8
# ###                 Energy Intensity Extract 1970-2021

import pandas as pd
from gssutils import *

metadata = Scraper(seed='info.json')
metadata.dataset.family = 'climate-change'
metadata.dataset.title = 'Energy Intensity Extract 1970 - 2021'
metadata.dataset.contactPoint = "energy.stats@beis.gov.uk"

distribution = metadata.distribution(mediaType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                     title=lambda x: "ECUK 2022: Energy intensity data tables (Excel)"
                                     in x,
                                     )                                   

tabs = {tab.name: tab for tab in distribution.as_databaker()}

# +
tidied_sheets = []

# from table I2
tab = tabs['Table I2']
unwanted_cells = tab.excel_ref("A59").expand(RIGHT).expand(DOWN).is_not_blank()
unwanted_cells_1 = tab.excel_ref("E8").expand(RIGHT).expand(DOWN).is_not_blank()
unwanted_cells_2 = tab.excel_ref("E7").expand(RIGHT).expand(DOWN).is_not_blank()
year = tab.excel_ref("A7").expand(DOWN).is_not_blank().is_not_whitespace() - unwanted_cells
measure_type = tab.excel_ref("B7").expand(RIGHT).is_not_blank() - unwanted_cells_2
sector = "road"
unit = "kilotonnes of oil equivalent"
observations = tab.excel_ref("B8").expand(DOWN).expand(RIGHT).is_not_blank().is_not_whitespace() - unwanted_cells_1

dimensions = [
            HDim(year, 'Year', CLOSEST, ABOVE),
            HDim(measure_type, 'Measure Type', DIRECTLY, ABOVE),
            HDimConst("Sector", sector),
            HDimConst("Unit", unit)
        ]

tidy_sheet = ConversionSegment(tab, dimensions, observations)
tab_I2 = tidy_sheet.topandas()

# from table I3
tab = tabs["Table I3"]
unwanted_cells = tab.excel_ref("A58").expand(RIGHT).expand(DOWN).is_not_blank()
unwanted_cells_1 = tab.excel_ref("E6").expand(RIGHT).expand(DOWN).is_not_blank()
unwanted_cells_2 = tab.excel_ref("E5").expand(RIGHT).expand(DOWN).is_not_blank()
year = tab.excel_ref("A5").expand(DOWN).is_not_blank().is_not_whitespace() - unwanted_cells
measure_type = tab.excel_ref("B5").expand(RIGHT).is_not_blank() - unwanted_cells_2
sector = "household"
unit = "kilotonnes of oil equivalent"
observations = tab.excel_ref("B6").expand(DOWN).expand(RIGHT).is_not_blank().is_not_whitespace() - unwanted_cells_1

dimensions = [
            HDim(year, 'Year', CLOSEST, ABOVE),
            HDim(measure_type, 'Measure Type', DIRECTLY, ABOVE),
            HDimConst("Sector", sector),
            HDimConst("Unit", unit)
        ]

tidy_sheet = ConversionSegment(tab, dimensions, observations)
tab_I3 = tidy_sheet.topandas()

# from table I4
tab = tabs['Table I4']        
unwanted_cells = tab.excel_ref("A60").expand(RIGHT).expand(DOWN).is_not_blank()
unwanted_cells_1 = tab.excel_ref("CG8").expand(RIGHT).expand(DOWN).is_not_blank()
unwanted_cells_2 = tab.excel_ref("CG7").expand(RIGHT).expand(DOWN).is_not_blank()
year = tab.excel_ref("CC7").expand(DOWN).is_not_blank().is_not_whitespace() - unwanted_cells
measure_type = tab.excel_ref("CD7").expand(RIGHT).is_not_blank() - unwanted_cells_2
sector = "industrial"
unit = "kilotonnes of oil equivalent"
observations = tab.excel_ref("CD8").expand(DOWN).expand(RIGHT).is_not_blank().is_not_whitespace() - unwanted_cells_1

dimensions = [
            HDim(year, 'Year', CLOSEST, ABOVE),
            HDim(measure_type, 'Measure Type', DIRECTLY, ABOVE),
            HDimConst("Sector", sector),
            HDimConst("Unit", unit)
        ]

tidy_sheet = ConversionSegment(tab, dimensions, observations)
tab_I4 = tidy_sheet.topandas()

# from table I5
tab = tabs['Table I5']             
unwanted_cells_1 = tab.excel_ref("U8").expand(RIGHT).expand(DOWN).is_not_blank()
unwanted_cells_2 = tab.excel_ref("U7").expand(RIGHT).expand(DOWN).is_not_blank()
year = tab.excel_ref("Q7").expand(DOWN).is_not_blank().is_not_whitespace()
measure_type = tab.excel_ref("R7").expand(RIGHT).is_not_blank() - unwanted_cells_2
sector = "services"
unit = "kilotonnes of oil equivalent"
observations = tab.excel_ref("R8").expand(DOWN).expand(RIGHT).is_not_blank().is_not_whitespace() - unwanted_cells_1

dimensions = [
            HDim(year, 'Year', CLOSEST, ABOVE),
            HDim(measure_type, 'Measure Type', DIRECTLY, ABOVE),
            HDimConst("Sector", sector),
            HDimConst("Unit", unit)
        ]

tidy_sheet = ConversionSegment(tab, dimensions, observations)
tab_I5 = tidy_sheet.topandas()

# +
tab_I2.replace({'Consumption (ktoe)': 'Road Passenger Consumption',
        'Output (billion passenger kilometres)': 'Output',
       'Energy consumption per billion passenger kilometres (ktoe)': 'Energy consumption per unit of output'
       }, inplace=True)

tab_I3.replace({'Total Final Consumption (ktoe)': 'Total Final Domestic Consumption',
                "No Households ('000s)": 'No Houeholds 000s',
                'Consumption per household (ktoe)': 'Consumption Per Household'
                }, inplace=True)

tab_I4.replace({'Consumption (ktoe)': 'Industrial Consumption',
                'Output': 'Industrial Output',
                'Consumption per unit of output (ktoe)': 'Consumption Per Unit of Unit'
                }, inplace=True)

tab_I5.replace({'Consumption (ktoe)': 'Service Consumption',
                'Output': 'Service Output',
                'Consumption per unit of output (ktoe)': 'Energy Consumption Per Unit of Unit 1'
                }, inplace=True)
# -

df = tidied_sheets.append(tab_I2)
df = tidied_sheets.append(tab_I3)
df = tidied_sheets.append(tab_I4)
df = tidied_sheets.append(tab_I5)

df = pd.concat(tidied_sheets, sort=True).fillna('')
df = df.rename(columns={'OBS': 'Value'})
df.replace({'2008 3': '2008'}, inplace=True)
df['Year'] = df['Year'].astype(float).astype(int)
df['Value'] = df['Value'].astype(str).astype(float).round(2)
df['Measure Type'] = df['Measure Type'].apply(pathify)
df['Unit'] = df['Unit'].apply(pathify)
df = df[['Year', 'Sector', 'Measure Type', 'Unit', 'Value']]

df.to_csv('observations.csv', index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')
