# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.10.2
#   kernelspec:
#     display_name: Python 3.8.8 64-bit
#     name: python3
# ---

# ## BEIS-Supplementary-tables-2019-UK-greenhouse-gas-emissions-by-Standard-Industrial-Classification

import json
import pandas as pd
from gssutils import *

cubes = Cubes("info.json")

info = json.load(open("info.json"))
landingPage = info["landingPage"]

metadata = Scraper(seed="info.json")

distribution = metadata.distributions[-4]

tabs = distribution.as_databaker()

#

contents = tabs[0]
titles = contents.excel_ref('B13').expand(DOWN) 
title_list = [title.value for title in titles]

trace = TransformTrace()

# +
i = 0
for tab in tabs:
	tab_list = [tab.name for tab in tabs]
	if tab.name in tab_list[1:-1]:
		title = title_list[i]
		print(tab.name, title) 
		metadata.dataset.title = title
		columns = ['SIC Group', 'Section', 'Section Name', 'Group Name', 'Year', 'Measure Type', 'Unit']
		trace.start(title, tab, columns, distribution.downloadURL) 
		section = tab.excel_ref('A4').expand(DOWN) - tab.excel_ref('A27').expand(DOWN)
		section_name = tab.excel_ref('C4').expand(DOWN) - tab.excel_ref('C27').expand(DOWN) 
		year = tab.excel_ref('D3').expand(RIGHT).is_not_blank()
		observations = section_name.fill(RIGHT).is_not_blank()

		dimensions = [
					HDim(section, 'Section', CLOSEST, UP),
					HDim(section_name, 'Section Name', DIRECTLY, LEFT),
					HDim(year, 'Period', DIRECTLY, ABOVE),
					HDimConst('Unit', "ktCO2e")
				]

		tidy_sheet = ConversionSegment(tab, dimensions, observations)
		table = tidy_sheet.topandas()
		trace.store('dataframe' + tab.name, table)

		bottom_block = tab.excel_ref('A164').expand(RIGHT).expand(DOWN)
		sic_group = tab.excel_ref('A31').expand(DOWN) - bottom_block
		section2 = tab.excel_ref('B31').expand(DOWN) - bottom_block 
		group_name = tab.excel_ref('C31').expand(DOWN) - bottom_block	
		year2 = tab.excel_ref('D30').expand(RIGHT).is_not_blank()
		observations2 = group_name.fill(RIGHT).is_not_blank()	

		dimensions2 = [
					HDim(sic_group, 'SIC(07)Group', CLOSEST, UP),
					HDim(section2, 'Section', CLOSEST, UP),
					HDim(group_name, 'Group Name', DIRECTLY, LEFT),	
					HDim(year2, 'Period', DIRECTLY, ABOVE),
					HDimConst('Unit', "ktCO2e")
				]

		tidy_sheet2 = ConversionSegment(tab, dimensions2, observations2)
		table2 = tidy_sheet2.topandas()
		trace.store('dataframe' + tab.name, table2)

		df = trace.combine_and_trace(title, 'dataframe' + tab.name).fillna(' ')
		df.rename(columns= {'OBS': 'Value'}, inplace=True)
		df['Period'] = df['Period'].str.replace('\.0', '')
		df['Value'] = df['Value'].astype(str).astype(float).round(1)
	
		df = df[['SIC(07)Group', 'Section', 'Section Name', 'Group Name', 'Period', 'Unit', 'Value']]

		for col in df.columns.values.tolist()[1:4]:
			df[col] = df[col].apply(pathify)

		cubes.add_cube(metadata, df, metadata.dataset.title)
		i += 1

	elif tab.name == '8.9':
		title = title_list[i] 
		print(tab.name, title)

		metadata.dataset.title = title
		columns = ['Section', 'SIC(07)Group', 'Group Name', 'National Communication Sector', 'Period', 'Unit', 'Value']
		trace.start(title, tab, columns, distribution.downloadURL) 
		section = tab.excel_ref('A4').expand(DOWN).is_not_blank() - tab.excel_ref('A403').expand(DOWN)
		sic_group = tab.excel_ref('B4').expand(DOWN).is_not_blank() - tab.excel_ref('B403').expand(DOWN)
		group_name = tab.excel_ref('C4').expand(DOWN).is_not_blank() - tab.excel_ref('C403').expand(DOWN) 
		ncs = tab.excel_ref('D4').expand(DOWN) - tab.excel_ref('D403').expand(DOWN) 
		year = tab.excel_ref('E3').expand(RIGHT).is_not_blank()
		observations = ncs.fill(RIGHT).is_not_blank()

		dimensions = [	
					HDim(section, 'Section', CLOSEST,ABOVE),
					HDim(sic_group, 'SIC(07)Group', CLOSEST,ABOVE), 
					HDim(group_name, 'Group Name', CLOSEST,ABOVE),
					HDim(ncs, 'National Communication Sector', DIRECTLY, LEFT),
					HDim(year, 'Period', DIRECTLY, ABOVE),
					HDimConst('Unit', "ktCO2e")
				]

		tidy_sheet = ConversionSegment(tab, dimensions, observations)
		table = tidy_sheet.topandas()
		trace.store('dataframe' + tab.name, table)

		df = trace.combine_and_trace(title, 'dataframe' + tab.name).fillna(' ')
		df.rename(columns= {'OBS': 'Value'}, inplace=True)
		df['Period'] = df['Period'].str.replace('\.0', '')
		df['Value'] = df['Value'].astype(str).astype(float).round(1)
		df = df[['Section', 'SIC(07)Group', 'Group Name', 'National Communication Sector', 'Period', 'Unit', 'Value']]
		for col in ['Section', 'Group Name', 'National Communication Sector']:
			df[col] = df[col].apply(pathify)

		cubes.add_cube(metadata, df, metadata.dataset.title)

cubes.output_all()
