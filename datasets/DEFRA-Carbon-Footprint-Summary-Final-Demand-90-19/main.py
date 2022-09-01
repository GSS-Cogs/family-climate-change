#!/usr/bin/env python
# coding: utf-8
#         DEFRA-Carbon-Footprint-Summary-Final-Demand-90-19

import pandas as pd
from gssutils import *

metadata = Scraper(seed='info.json')

distribution = metadata.distribution(
    mediaType="application/vnd.oasis.opendocument.spreadsheet",
    title=lambda x: "UK full dataset 1990 - 2019, including conversion factors by SIC code"
    in x,
)

title = distribution.title

tabs = {tab.name: tab for tab in distribution.as_databaker()}

# +
tidied_sheets = []
for name, tab in tabs.items():
    datasetTitle = 'UK full dataset 1990 - 2019, including conversion factors by SIC code'
    
    if 'Summary_final_demand_90-19' not in name:
        continue
    print(name)

    # Greenhouse Gas emissions - GHG - Ktonnes CO2e	
    unwanted_cell = tab.excel_ref("A34").expand(DOWN).expand(RIGHT)
    period = tab.excel_ref("B4").expand(DOWN).is_not_blank().is_not_whitespace() - unwanted_cell
    final_demand = tab.excel_ref("C2").expand(RIGHT)
    final_demand_breakdown = tab.excel_ref("C3").expand(RIGHT).is_not_blank().is_not_whitespace()
    observations = tab.excel_ref("C4").expand(DOWN).expand(RIGHT).is_not_blank() - unwanted_cell
    measure = 'Greenhouse gas emissions'
    unit = 'kt CO2e'
    
    dimensions = [
        HDim(period,'Period',DIRECTLY,LEFT),
        HDim(final_demand,'Final Demand',DIRECTLY, ABOVE),
        HDim(final_demand_breakdown, 'Final Demand Breakdown',DIRECTLY,ABOVE),
        HDimConst("Measure", measure),
        HDimConst("Unit", unit)
    ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations) 
    tidied_sheets.append(tidy_sheet.topandas())


# from Carbon Dioxide Emission
    period = tab.excel_ref("B38").expand(DOWN).is_not_blank().is_not_whitespace()
    final_demand = tab.excel_ref("C36").expand(RIGHT)
    final_demand_breakdown = tab.excel_ref("C37").expand(RIGHT)
    observations = tab.excel_ref("C38").expand(DOWN).expand(RIGHT).is_not_blank().is_not_whitespace()
    measure = 'Carbon dioxide emissions'
    unit = 'kt CO2'

    dimensions = [
        HDim(period,'Period',DIRECTLY,LEFT),
        HDim(final_demand,'Final Demand',DIRECTLY, ABOVE),
        HDim(final_demand_breakdown, 'Final Demand Breakdown',DIRECTLY,ABOVE),
        HDimConst("Measure", measure),
        HDimConst("Unit", unit)
    ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations) 
    # savepreviewhtml(tidy_sheet,fname=tab.name + "Preview.html")
    tidied_sheets.append(tidy_sheet.topandas())
# -

df = pd.concat(tidied_sheets, sort=True)

df["Final Demand"] = df.apply(lambda x: "Not Applicable" if x["Final Demand"] == '' else x["Final Demand"], axis = 1)

df["Final Demand Breakdown"] = df.apply(lambda x: "Not Applicable" if x["Final Demand Breakdown"] == '' else x["Final Demand Breakdown"], axis = 1)

df = df.replace({'Final Demand' : {'Households' : 'FD1',
                                   'Households direct' : 'FD1',
                                   'Non-profit institutions serving households' : 'FD2',
                                   'Central Government' : 'FD3',
                                   'Local Government' : 'FD4',
                                   'Gross fixed capital formation' : 'FD5',
                                   'Valuables' : 'FD6',
                                   'Changes in inventories' : 'FD7',
                                   'Total' : 'all'},
                 'Final Demand Breakdown' : {'Total' : 'all'}}) 

df.rename(columns={'OBS' : 'Value'}, inplace=True)

df['Period'] = df['Period'].astype(float).astype(int)


df['Period'] = df['Period'].map(lambda x: 'year/' + str(x))


df['Final Demand Breakdown'] = df['Final Demand Breakdown'].map(lambda x: pathify(x))

df = df[['Period', 'Final Demand', 'Final Demand Breakdown', 'Measure', 'Unit', 'Value']]

df.to_csv('observations.csv', index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')
