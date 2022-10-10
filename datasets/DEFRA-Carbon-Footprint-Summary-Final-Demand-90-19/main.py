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

tabs = distribution.as_databaker()

# +
tidied_sheets = []

for tab in tabs:    
    if tab.name == 'Summary_final_demand_90-19':

        # Greenhouse Gas emissions - GHG - Ktonnes CO2e	
        unwanted_cell = tab.excel_ref("A34").expand(DOWN).expand(RIGHT)
        period = tab.excel_ref("B4").expand(DOWN).is_not_blank().is_not_whitespace() - unwanted_cell
        final_demand = tab.excel_ref("C2").expand(RIGHT) - tab.excel_ref("L2").expand(RIGHT)
        final_demand_breakdown = tab.excel_ref("C3").expand(RIGHT) - tab.excel_ref("L3").expand(RIGHT)
        observations = period.waffle(final_demand_breakdown)
        measure = 'Greenhouse gas emissions'
        unit = 'kt CO2e'
        
        dimensions = [
            HDim(period,'Period',DIRECTLY,LEFT),
            HDim(final_demand, 'Final Demand Code',DIRECTLY, ABOVE),
            HDim(final_demand_breakdown, 'Final Demand Breakdown',DIRECTLY,ABOVE),
            HDimConst("Measure", measure),
            HDimConst("Unit", unit)
        ]
        tidy_sheet = ConversionSegment(tab, dimensions, observations) 
        tidied_sheets.append(tidy_sheet.topandas())

        # from Carbon Dioxide Emission
        period = tab.excel_ref("B38").expand(DOWN).is_not_blank().is_not_whitespace()
        final_demand = tab.excel_ref("C36").expand(RIGHT) - tab.excel_ref("L36").expand(RIGHT)
        final_demand_breakdown = tab.excel_ref("C37").expand(RIGHT) - tab.excel_ref("L37").expand(RIGHT)
        observations = period.waffle(final_demand_breakdown)
        measure = 'Carbon dioxide emissions'
        unit = 'kt CO2'

        dimensions = [
            HDim(period,'Period',DIRECTLY,LEFT),
            HDim(final_demand, 'Final Demand Code',DIRECTLY, ABOVE),
            HDim(final_demand_breakdown, 'Final Demand Breakdown',DIRECTLY,ABOVE),
            HDimConst("Measure", measure),
            HDimConst("Unit", unit)
        ]
        tidy_sheet = ConversionSegment(tab, dimensions, observations) 
        tidied_sheets.append(tidy_sheet.topandas())
        # savepreviewhtml(tidy_sheet,fname=tab.name + "Preview.html")
# -

df = pd.concat(tidied_sheets).fillna('')

df = df.replace({'Final Demand Breakdown': {
                                   'Non-profitinstitutions servinghouseholds' : 'Non-profit institutions serving households',
                                   'Gross fixedcapitalformation' : 'Gross fixed capital formation',
                                   '' : 'Total'}}) 

# +
df['Final Demand Code'] = df.apply(lambda x: 'UK FD 1' if x['Final Demand Breakdown'] == 'Households direct' else x['Final Demand Code'], axis=1)
df["Final Demand Code"] = df["Final Demand Code"].str.replace("UK ", "")

indexNames = df[df['Final Demand Breakdown'] == 'Total'].index
df.drop(indexNames, inplace=True)

indexNames = df[df['Final Demand Code'] == 'Total'].index
df.drop(indexNames, inplace=True)

df.drop(columns ='Final Demand Code', inplace=True)
# -

df.rename(columns={'OBS' : 'Value'}, inplace=True)
df["Value"] = df["Value"].astype(float).round(3)
df['Period'] = df['Period'].astype(float).astype(int)
df['Period'] = df['Period'].map(lambda x: 'year/' + str(x))
df = df.drop_duplicates()

# +
for col in ['Final Demand Breakdown', 'Measure', 'Unit']:
    try:
        df[col] = df[col].apply(pathify)
    except Exception as err:
        raise Exception("Failed to pathify column '{}'.".format(col)) from err

df = df[['Period', 'Final Demand Breakdown', 'Measure', 'Unit', 'Value']]
# -

df.to_csv('observations.csv', index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')
