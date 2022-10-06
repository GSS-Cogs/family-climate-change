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

metadata.dataset.title = "Carbon Footprint - Summary Final Demand 90-19"
metadata.dataset.comment = "Greenhouse gas emissions by; region, households, consumables, services"

tabs = {tab.name: tab for tab in distribution.as_databaker()}

# +
tidied_sheets = []
for name, tab in tabs.items():
    
    if 'Summary_final_demand_90-19' not in name:
        continue

    # Greenhouse Gas emissions - GHG - Ktonnes CO2e	
    unwanted_cell = tab.excel_ref("A34").expand(DOWN).expand(RIGHT)
    period = tab.excel_ref("B4").expand(DOWN).is_not_blank().is_not_whitespace() - unwanted_cell
    final_demand_breakdown = tab.excel_ref("C3").expand(RIGHT).is_not_blank().is_not_whitespace()
    observations = tab.excel_ref("C4").expand(DOWN).expand(RIGHT).is_not_blank() - unwanted_cell
    measure = 'Greenhouse gas emissions'
    unit = 'kt CO2e'
    
    dimensions = [
        HDim(period,'Period',DIRECTLY,LEFT),
        HDim(final_demand_breakdown, 'Final Demand Breakdown',DIRECTLY,ABOVE),
        HDimConst("Measure", measure),
        HDimConst("Unit", unit)
    ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations) 
    tidied_sheets.append(tidy_sheet.topandas())

# from Carbon Dioxide Emission
    period = tab.excel_ref("B38").expand(DOWN).is_not_blank().is_not_whitespace()
    final_demand_breakdown = tab.excel_ref("C37").expand(RIGHT)
    observations = tab.excel_ref("C38").expand(DOWN).expand(RIGHT).is_not_blank().is_not_whitespace()
    measure = 'Carbon dioxide emissions'
    unit = 'kt CO2'

    dimensions = [
        HDim(period,'Period',DIRECTLY,LEFT),
        HDim(final_demand_breakdown, 'Final Demand Breakdown',DIRECTLY,ABOVE),
        HDimConst("Measure", measure),
        HDimConst("Unit", unit)
    ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations) 
    tidied_sheets.append(tidy_sheet.topandas())
    # savepreviewhtml(tidy_sheet,fname=tab.name + "Preview.html")
# -

df = pd.concat(tidied_sheets, sort=True)

df = df.replace({'Final Demand Breakdown': {
                                   'Non-profitinstitutions servinghouseholds' : 'Non-profit institutions serving households',
                                   'Gross fixedcapitalformation' : 'Gross fixed capital formation',
                                   '' : 'Total'}}) 

indexNames = df[df['Final Demand Breakdown'] == 'Total'].index
df.drop(indexNames, inplace=True)

df.rename(columns={'OBS' : 'Value'}, inplace=True)
df['Period'] = df['Period'].astype(float).astype(int)
df['Period'] = df['Period'].map(lambda x: 'year/' + str(x))
df["Value"] = df["Value"].astype(float).round(3)
df = df.drop_duplicates()

for col in ['Measure', 'Unit']:
    try:
        df[col] = df[col].apply(pathify)
    except Exception as err:
        raise Exception("Failed to pathify column '{}'.".format(col)) from err

df = df[['Period', 'Final Demand Breakdown', 'Measure', 'Unit', 'Value']]

df.to_csv('observations.csv', index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')
