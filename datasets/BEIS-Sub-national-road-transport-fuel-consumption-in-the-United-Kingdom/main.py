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

# ## BEIS-Sub-national-road-transport-fuel-consumption-in-the-United-Kingdom

import json
import pandas as pd
from gssutils import *

cubes = Cubes('info.json')
info = json.load(open('info.json'))
landingPage = info['landingPage']
landingPage

metadata = Scraper(seed='info.json')

distribution = metadata.distribution(title = lambda x: "Sub-national road transport fuel consumption statistics, 2005-2019 (Excel)" in x, latest = True)

tabs = distribution.as_databaker()

# +
tidied_sheets = []
for tab in tabs[1:-2]:
	metadata.dataset.title = 'Road transport energy consumption at regional and local authority level, 2005-2019'
	code = tab.excel_ref('A5').expand(DOWN) - tab.excel_ref('A403').expand(DOWN)
	city = tab.excel_ref('B5').expand(DOWN) - tab.excel_ref('B403').expand(DOWN)
	road = tab.excel_ref('C4').expand(RIGHT).is_not_blank() - tab.excel_ref('AE4').expand(RIGHT)
	vehicle = tab.excel_ref('C3').expand(RIGHT).is_not_blank() - tab.excel_ref('AE3').expand(RIGHT)
	purpose = tab.excel_ref('C2').expand(RIGHT).is_not_blank(	) - tab.excel_ref('AE2').expand(RIGHT)
	observations = tab.excel_ref('C5').expand(RIGHT).expand(DOWN).is_not_blank() - tab.excel_ref('AE5').expand(RIGHT).expand(DOWN) 

	dimensions = [
				HDim(city, 'City', DIRECTLY, LEFT),
				HDim(code, 'City Code', DIRECTLY, LEFT),
				HDim(road, 'Road Type', DIRECTLY, ABOVE),
				HDim(vehicle, 'Vehicle', CLOSEST, LEFT),
				HDim(purpose, 'Purpose', CLOSEST, LEFT),
				HDimConst('Year', tab.name),
				HDimConst('Unit', "Thousand tonnes of oil equivalent (ktoe)")
			]
	tidy_sheet = ConversionSegment(tab, dimensions, observations)
	table = tidy_sheet.topandas()
	tidied_sheets.append(table)

df = pd.concat(tidied_sheets, sort=True).fillna('')

df.rename(columns={'OBS' : 'Value'}, inplace=True)
df['Value'] = pd.to_numeric(df['Value'], downcast='float')
df['Value'] = df['Value'].astype(str).astype(float).round(2)

for col in df.columns.tolist():
	if col in ['City', 'Road Type', 'Vehicle', 'Purpose', 'Unit']:
		df[col] = df[col].apply(pathify)
df = df[['Year', 'City Code', 'City', 'Road Type', 'Vehicle', 'Purpose', 'Unit', 'Value']]

cubes.add_cube(metadata, df.drop_duplicates(), metadata.dataset.title)
cubes.output_all()	
