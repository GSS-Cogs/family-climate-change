# -*- coding: utf-8 -*-
# # ONS-Woodland-natural-capital-accounts

# +
import pandas as pd
from gssutils import *
import json
import string
import numpy as np

info = json.load(open('info.json'))
landingPage = info['landingPage']
landingPage

scraper = Scraper(seed='info.json')
scraper

trace = TransformTrace()
cubes = Cubes('info.json')

dist = scraper.distribution(latest=True, mediaType=Excel)
datasetTitle = info['title']
dist
datasetTitle

tabs_name = ['Physical flows', 'Annual value', 'Asset value']
tabs = {tab: tab for tab in dist.as_databaker() if tab.name in tabs_name}
if len(set(tabs_name) - {x.name for x in tabs}) != 0:
    raise ValueError(f'Aborting. A tab named {set(tabs_name) - {x.name for x in tabs} } required but not found')


def left(s, amount):
    return s[:amount]


def right(s, amount):
    return s[-amount:]


def mid(s, offset, amount):
    return s[offset:offset+amount]


def cellLoc(cell):
    return right(str(cell), len(str(cell)) - 2).split(" ", 1)[0]


def col2num(col):
    num = 0
    for c in col:
        if c in string.ascii_letters:
            num = num * 26 + (ord(c.upper()) - ord('A')) + 1
    return num


def colnum_string(n):
    string = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        string = chr(65 + remainder) + string
    return string


def excelRange(bag):
    xvalues = []
    yvalues = []
    for cell in bag:
        coordinate = cellLoc(cell)
        xvalues.append(''.join([i for i in coordinate if not i.isdigit()]))
        yvalues.append(int(''.join([i for i in coordinate if i.isdigit()])))
    high = 0
    low = 0
    for i in xvalues:
        if col2num(i) >= high:
            high = col2num(i)
        if low == 0:
            low = col2num(i)
        elif col2num(i) < low:
            low = col2num(i)
        highx = colnum_string(high)
        lowx = colnum_string(low)
    highy = str(max(yvalues))
    lowy = str(min(yvalues))
    return '{' + lowx + lowy + '-' + highx + highy + '}'


def filter_country(column_value):
    if column_value.lower() == 'england':
        return 'England'
    elif column_value.lower() == 'scotland':
        return 'Scotland'
    elif column_value.lower() == 'wales':
        return 'Wales'
    elif column_value.lower() == 'northern ireland':
        return 'Northern Ireland'
    else:
        return None


for tab in tabs:
    print(tab.name)
    if tab.name == 'Physical flows':
        columns = ['Period', 'Measure Type', 'Physical Flow']
        trace.start(datasetTitle, tab, columns, dist.downloadURL)

        period = tab.excel_ref('C4').expand(RIGHT).is_not_blank()
        trace.Period('Defined from cell range: {}', var=excelRange(period))

        measure_type = tab.excel_ref('B5').expand(DOWN).is_not_blank()
        trace.Measure_Type('Defined from cell range: {}', var=excelRange(measure_type))

        physical_flow = tab.excel_ref('A4').expand(DOWN).is_not_blank()
        trace.Physical_Flow('Defined from cell range: {}', var=excelRange(physical_flow))

        observations = tab.excel_ref('C5').expand(DOWN).expand(RIGHT).is_not_blank()

        dimensions = [
            HDim(period, 'Period', DIRECTLY, ABOVE),
            HDim(measure_type, 'Measure Type', DIRECTLY, LEFT),
            HDim(physical_flow, 'Physical Flow', DIRECTLY, LEFT)
        ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        trace.with_preview(tidy_sheet)
        savepreviewhtml(tidy_sheet, fname=f'{tab.name}_Preview.html')
        trace.store(f'combined_dataframe_table_physical_flows', tidy_sheet.topandas())
    if tab.name == 'Annual value':
        columns = ['Period', 'Measure Type', 'Physical Flow']
        trace.start(datasetTitle, tab, columns, dist.downloadURL)

        period = tab.excel_ref('B4').expand(RIGHT).is_not_blank()
        trace.Period('Defined from cell range: {}', var=excelRange(period))

        measure_type = tab.excel_ref('A4')
        trace.Measure_Type('Defined from cell value: {}', var=cellLoc(measure_type))

        physical_flow = tab.excel_ref('A5').expand(DOWN).is_not_blank()
        trace.Physical_Flow('Defined from cell range: {}', var=excelRange(physical_flow))

        observations = tab.excel_ref('B5').expand(DOWN).expand(RIGHT).is_not_blank()

        dimensions = [
            HDim(period, 'Period', DIRECTLY, ABOVE),
            HDim(measure_type, 'Measure Type', CLOSEST, ABOVE),
            HDim(physical_flow, 'Physical Flow', DIRECTLY, LEFT)
        ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        trace.with_preview(tidy_sheet)
        savepreviewhtml(tidy_sheet, fname=f'{tab.name}_Preview.html')
        trace.store(f'combined_dataframe_table_annual_value', tidy_sheet.topandas())
    if tab.name == 'Asset value':
        columns = ['Period', 'Measure Type', 'Physical Flow', 'Country']
        trace.start(datasetTitle, tab, columns, dist.downloadURL)

        period = tab.excel_ref('B4')
        trace.Period('Defined from cell value: {}', var=cellLoc(period))

        measure_type = tab.excel_ref('A4')
        trace.Measure_Type('Defined from cell value: {}', var=cellLoc(measure_type))

        physical_flow = tab.excel_ref('A5').expand(DOWN).is_not_blank()
        trace.Physical_Flow('Defined from cell range: {}', var=excelRange(physical_flow))

        country = tab.excel_ref('B17').expand(RIGHT).is_not_blank()
        trace.Country('Defined from cell range: {}', var=excelRange(country))

        observations = tab.excel_ref('B5').expand(DOWN).expand(RIGHT).is_not_blank()

        dimensions = [
            HDim(period, 'Period', CLOSEST, ABOVE),
            HDim(measure_type, 'Measure Type', CLOSEST, ABOVE),
            HDim(physical_flow, 'Physical Flow', DIRECTLY, LEFT),
            HDim(country, 'Country', DIRECTLY, ABOVE)
        ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        trace.with_preview(tidy_sheet)
        savepreviewhtml(tidy_sheet, fname=f'{tab.name}_Preview.html')
        trace.store(f'combined_dataframe_table_asset_value', tidy_sheet.topandas())

df_tbl_physical_flows = trace.combine_and_trace(datasetTitle, 'combined_dataframe_table_physical_flows')
trace.add_column('Value')
trace.Value('Rename databaker column OBS to Value')
df_tbl_physical_flows.rename(columns={'OBS': 'Value', 'DATAMARKER': 'Marker'}, inplace=True)

df_tbl_physical_flows['Country'] = df_tbl_physical_flows['Physical Flow'].apply(filter_country)
df_tbl_physical_flows['Country'] = df_tbl_physical_flows['Country'].ffill()
df_tbl_physical_flows['Country'] = df_tbl_physical_flows['Country'].fillna('United Kingdom')

df_tbl_physical_flows_country_idx = df_tbl_physical_flows[df_tbl_physical_flows['Physical Flow'].isin(['England', 'Scotland', 'Wales', 'Northern Ireland'])].index
df_tbl_physical_flows.drop(df_tbl_physical_flows_country_idx , inplace=True)

df_tbl_physical_flows['Period'] = pd.to_numeric(df_tbl_physical_flows['Period'], errors='coerce').astype('Int64')
df_tbl_physical_flows['Value'] = pd.to_numeric(df_tbl_physical_flows['Value'], errors='coerce').astype('float64').replace(np.nan, 'None')
df_tbl_physical_flows['Marker'] = df_tbl_physical_flows['Physical Flow']

df_tbl_physical_flows = df_tbl_physical_flows[['Period', 'Country', 'Physical Flow', 'Marker', 'Value', 'Measure Type']]

df_tbl_annual_value = trace.combine_and_trace(datasetTitle, 'combined_dataframe_table_annual_value')
trace.add_column('Value')
trace.Value('Rename databaker column OBS to Value')
df_tbl_annual_value.rename(columns={'OBS': 'Value', 'DATAMARKER': 'Marker'}, inplace=True)

df_tbl_annual_value['Country'] = df_tbl_annual_value['Physical Flow'].apply(filter_country)
df_tbl_annual_value['Country'] = df_tbl_annual_value['Country'].ffill()
df_tbl_annual_value['Country'] = df_tbl_annual_value['Country'].fillna('United Kingdom')

df_tbl_annual_value_country_idx = df_tbl_annual_value[df_tbl_annual_value['Physical Flow'].isin(['England', 'Scotland', 'Wales', 'Northern Ireland'])].index
df_tbl_annual_value.drop(df_tbl_annual_value_country_idx , inplace=True)

df_tbl_annual_value['Period'] = pd.to_numeric(df_tbl_annual_value['Period'], errors='coerce').astype('Int64')
df_tbl_annual_value['Measure Type'] = df_tbl_annual_value['Measure Type'].apply(lambda x : str(x).rstrip(x[-1]))
df_tbl_annual_value['Value'] = df_tbl_annual_value.apply(lambda x: None if x['Marker']=='-' else x['Value'], axis=1)
df_tbl_annual_value['Value'] = pd.to_numeric(df_tbl_annual_value['Value'], errors='coerce').astype('float64').replace(np.nan, 'None')
df_tbl_annual_value['Marker'] = df_tbl_annual_value['Physical Flow']

df_tbl_annual_value = df_tbl_annual_value[['Period', 'Country', 'Physical Flow', 'Marker', 'Value', 'Measure Type']]

df_tbl_asset_value = trace.combine_and_trace(datasetTitle, 'combined_dataframe_table_asset_value')
trace.add_column('Value')
trace.Value('Rename databaker column OBS to Value')
df_tbl_asset_value.rename(columns={'OBS': 'Value', 'DATAMARKER': 'Marker'}, inplace=True)

df_tbl_asset_value_country_idx = df_tbl_asset_value[df_tbl_asset_value['Marker'].isin(['England', 'Scotland', 'Wales', 'Northern Ireland'])].index
df_tbl_asset_value.drop(df_tbl_asset_value_country_idx , inplace=True)
df_tbl_asset_value['Country'] = df_tbl_asset_value['Country'].fillna('United Kingdom')

df_tbl_asset_value['Period'] = pd.to_numeric(df_tbl_asset_value['Period'], errors='coerce').astype('Int64')
df_tbl_asset_value['Measure Type'] = df_tbl_asset_value['Measure Type'].apply(lambda x : str(x).rstrip(x[-1]))
df_tbl_asset_value['Value'] = pd.to_numeric(df_tbl_asset_value['Value'], errors='coerce').astype('float64').replace(np.nan, 'None')
df_tbl_asset_value['Marker'] = df_tbl_asset_value['Physical Flow']

df_tbl_asset_value = df_tbl_asset_value[['Period', 'Country', 'Physical Flow', 'Marker', 'Value', 'Measure Type']]
