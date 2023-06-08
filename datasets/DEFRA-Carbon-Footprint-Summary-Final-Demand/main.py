#!/usr/bin/env python
# coding: utf-8
#         DEFRA-Carbon-Footprint-Summary-Final-Demand
import pandas as pd
from gssutils import *

metadata = Scraper(seed='info.json')
distribution = metadata.distribution(latest=True)
distribution = metadata.distribution(
    mediaType="application/vnd.oasis.opendocument.spreadsheet",
    title=lambda x: "UK full dataset 1990 - 2020, including conversion factors by SIC code"
    in x,
)

tabs = distribution.as_databaker()

tidied_sheets = []
for tab in tabs:    
    if tab.name == 'Summary_final_demand_90-20':

        # Greenhouse Gas emissions - GHG - Ktonnes CO2e	
        unwanted_cell = tab.excel_ref("A35").expand(DOWN).expand(RIGHT)
        period = tab.excel_ref("B4").expand(DOWN).is_not_blank().is_not_whitespace() - unwanted_cell
        final_demand = tab.excel_ref("C2").expand(RIGHT) - tab.excel_ref("L2").expand(RIGHT)
        final_demand_breakdown = tab.excel_ref("C3").expand(RIGHT) - tab.excel_ref("L3").expand(RIGHT)
        observations = period.waffle(final_demand_breakdown)
        measure = 'greenhouse-gas-emissions'
        unit = 'kt-co2e'
        
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
        period = tab.excel_ref("B39").expand(DOWN).is_not_blank().is_not_whitespace()
        final_demand = tab.excel_ref("C37").expand(RIGHT) - tab.excel_ref("L37").expand(RIGHT)
        final_demand_breakdown = tab.excel_ref("C38").expand(RIGHT) - tab.excel_ref("L38").expand(RIGHT)
        observations = period.waffle(final_demand_breakdown)
        measure = 'carbon-dioxide-emissions'
        unit = 'kt-co2'

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

df = pd.concat(tidied_sheets).fillna('')

df = df.replace({'Final Demand Breakdown': {
                                   'Non-profitinstitutions servinghouseholds' : 'Non-profit institutions serving households',
                                   'Gross fixedcapitalformation' : 'Gross fixed capital formation',
                                   '' : 'Grand Total'}}) 

df['Final Demand Code'] = df.apply(lambda x: 'UK FD 1' if x['Final Demand Breakdown'] == 'Households direct' else x['Final Demand Code'], axis=1)
df["Final Demand Code"] = df["Final Demand Code"].str.replace("UK ", "")
df.drop(columns ='Final Demand Code', inplace=True)

# indexNames = df[df['Final Demand Breakdown'] == 'Total'].index
# df.drop(indexNames, inplace=True)

# indexNames = df[df['Final Demand Code'] == 'Total'].index
# df.drop(indexNames, inplace=True)

df["Final Demand Breakdown"] = df["Final Demand Breakdown"].apply(pathify)

df.rename(columns={'OBS' : 'Value', 'Period' : 'Year'}, inplace=True)
df["Value"] = df["Value"].astype(float).round(2)
df['Year'] = df['Year'].astype(float).astype(int)

df = df[['Year', 'Final Demand Breakdown', 'Measure', 'Unit', 'Value']]

metadata.dataset.issued = "2023-06-07T09:30:00.738324+00:00"
metadata.dataset.contactPoint = "mailto:enviro.statistics@defra.gov.uk"
metadata.dataset.title = "Carbon Footprint - Summary Final Demand"
metadata.dataset.comment = "Annual greenhouse gas and carbon dioxide emissions relating to UK consumption."
metadata.dataset.description = """
This publication looks at the carbon footprint for the UK.

The carbon footprint refers to emissions that are associated with the
consumption spending of UK/England's residents on goods and services,
wherever in the world these emissions arise along the supply chain, and those
which are directly generated by UK/England's households through private
motoring and burning fuel to heat homes. These emissions are often referred
to as 'consumption emissions' to distinguish them from estimates relating to
the emissions 'produced' within a country's territory or economic sphere.

"""

df.to_csv('observations.csv', index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')