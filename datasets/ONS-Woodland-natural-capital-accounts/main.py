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


def convert_category_datatype(df, columns_arr):
    for col in df.columns:
        if col in columns_arr:
            try:
                df[col] = df[col].astype('category')
            except ValueError as err:
                raise ValueError('Failed to convert category data type for column "{}".'.format(col)) from err


def pathify_columns(df, columns_arr):
    for col in df.columns:
        if col in columns_arr:
            try:
                df[col] = df[col].apply(lambda x: pathify(str(x)))
            except Exception as err:
                raise Exception('Failed to pathify column "{}".'.format(col)) from err


for tab in tabs:
    print(tab.name)
    if tab.name == 'Physical flows':
        columns = ['Period', 'Unit', 'Services', 'Service Type']
        trace.start(datasetTitle, tab, columns, dist.downloadURL)

        period = tab.excel_ref('C4').expand(RIGHT).is_not_blank()
        trace.Period('Defined from cell range: {}', var=excelRange(period))

        unit = tab.excel_ref('B5').expand(DOWN).is_not_blank()
        trace.Unit('Defined from cell range: {}', var=excelRange(unit))

        services = tab.excel_ref('A4').expand(DOWN).is_not_blank()
        trace.Services('Defined from cell range: {}', var=excelRange(services))

        service_type = 'Woodland'
        trace.Service_Type('Hardcoded as Woodland')

        observations = tab.excel_ref('C5').expand(DOWN).expand(RIGHT).is_not_blank()

        dimensions = [
            HDim(period, 'Period', DIRECTLY, ABOVE),
            HDim(unit, 'Unit', DIRECTLY, LEFT),
            HDim(services, 'Services', DIRECTLY, LEFT),
            HDimConst('Service Type', service_type)
        ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        trace.with_preview(tidy_sheet)
        savepreviewhtml(tidy_sheet, fname=f'{tab.name}_Preview.html')
        trace.store(f'combined_dataframe_table_physical_flows', tidy_sheet.topandas())
    if tab.name == 'Annual value':
        columns = ['Period', 'Unit', 'Physical Flow']
        trace.start(datasetTitle, tab, columns, dist.downloadURL)

        period = tab.excel_ref('B4').expand(RIGHT).is_not_blank()
        trace.Period('Defined from cell range: {}', var=excelRange(period))

        unit = tab.excel_ref('A4')
        trace.Unit('Defined from cell value: {}', var=cellLoc(unit))

        physical_flow = tab.excel_ref('A5').expand(DOWN).is_not_blank()
        trace.Physical_Flow('Defined from cell range: {}', var=excelRange(physical_flow))

        observations = tab.excel_ref('B5').expand(DOWN).expand(RIGHT).is_not_blank()

        dimensions = [
            HDim(period, 'Period', DIRECTLY, ABOVE),
            HDim(unit, 'Unit', CLOSEST, ABOVE),
            HDim(physical_flow, 'Physical Flow', DIRECTLY, LEFT)
        ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        trace.with_preview(tidy_sheet)
        savepreviewhtml(tidy_sheet, fname=f'{tab.name}_Preview.html')
        trace.store(f'combined_dataframe_table_annual_value', tidy_sheet.topandas())
    if tab.name == 'Asset value':
        columns = ['Period', 'Unit', 'Physical Flow', 'Country']
        trace.start(datasetTitle, tab, columns, dist.downloadURL)

        period = tab.excel_ref('B4')
        trace.Period('Defined from cell value: {}', var=cellLoc(period))

        unit = tab.excel_ref('A4')
        trace.Unit('Defined from cell value: {}', var=cellLoc(unit))

        physical_flow = tab.excel_ref('A5').expand(DOWN).is_not_blank()
        trace.Physical_Flow('Defined from cell range: {}', var=excelRange(physical_flow))

        country = tab.excel_ref('B17').expand(RIGHT).is_not_blank()
        trace.Country('Defined from cell range: {}', var=excelRange(country))

        observations = tab.excel_ref('B5').expand(DOWN).expand(RIGHT).is_not_blank()

        dimensions = [
            HDim(period, 'Period', CLOSEST, ABOVE),
            HDim(unit, 'Unit', CLOSEST, ABOVE),
            HDim(physical_flow, 'Physical Flow', DIRECTLY, LEFT),
            HDim(country, 'Country', DIRECTLY, ABOVE)
        ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        trace.with_preview(tidy_sheet)
        savepreviewhtml(tidy_sheet, fname=f'{tab.name}_Preview.html')
        trace.store(f'combined_dataframe_table_asset_value', tidy_sheet.topandas())

ons_geography_code_dict={'United Kingdom': 'K02000001', 'England':'E92000001', 'Wales':'W92000004', 'Northern Ireland':'N92000002', 'Scotland':'S92000003'}
physical_flow_dict={'Timber': 'Provisioning Services', 'Wood fuel':'Provisioning Services', 'Carbon sequestration':'Regulating Services',
                    'Pollution removal':'Regulating Services', 'Noise reduction':'Regulating Services', 'Recreation visits':'Cultural Services', 'Recreation (time at habitat)':'Cultural Services'}

df_tbl_physical_flows = trace.combine_and_trace(datasetTitle, 'combined_dataframe_table_physical_flows')
trace.add_column('Value')
trace.Value('Rename databaker column OBS to Value')
df_tbl_physical_flows.rename(columns={'OBS': 'Value', 'DATAMARKER': 'Marker'}, inplace=True)

df_tbl_physical_flows['Country'] = df_tbl_physical_flows['Services'].apply(filter_country)
df_tbl_physical_flows['Country'] = df_tbl_physical_flows['Country'].ffill()
df_tbl_physical_flows['Country'] = df_tbl_physical_flows['Country'].fillna('United Kingdom')
trace.add_column('Country')
trace.Country('Create Country Value based on country columns in Physical flows sheet')
df_tbl_physical_flows['ONS Geography Code'] = df_tbl_physical_flows['Country'].replace(ons_geography_code_dict)
trace.add_column('ONS Geography Code')
trace.ONS_Geography_Code("Create ONS Geography Code Value based on 'Country' column")
df_tbl_physical_flows_country_idx = df_tbl_physical_flows[df_tbl_physical_flows['Services'].isin(['England', 'Scotland', 'Wales', 'Northern Ireland'])].index
df_tbl_physical_flows.drop(df_tbl_physical_flows_country_idx , inplace=True)

df_tbl_physical_flows['Period'] = pd.to_numeric(df_tbl_physical_flows['Period'], errors='coerce').astype('Int64')
trace.Period("Format 'Period' column to decimal calendar year")

df_tbl_physical_flows['Value'] = pd.to_numeric(df_tbl_physical_flows['Value'], errors='coerce').astype('float64').replace(np.nan, 'None')
trace.Value("Change - DataMarker to 'None'")
trace.Value("Format 'Value' column to float64 value type")

df_tbl_physical_flows['Marker'] = df_tbl_physical_flows['Services']
trace.add_column('Marker')
trace.Marker("Create Marker Value based on 'Services' column")

df_tbl_physical_flows['Services'] = df_tbl_physical_flows['Marker'].replace(physical_flow_dict)
trace.Services('Create Services Value based on physical flow columns in Physical flows sheet')
trace.Service_Type('Hardcoded as Woodland')
df_tbl_physical_flows['Measure Type'] = df_tbl_physical_flows['Marker']
trace.add_column('Measure Type')
trace.Measure_Type("Create Measure Type Value based on 'Marker' column")

df_tbl_annual_value = trace.combine_and_trace(datasetTitle, 'combined_dataframe_table_annual_value')
trace.add_column('Value')
trace.Value('Rename databaker column OBS to Value')
df_tbl_annual_value.rename(columns={'OBS': 'Value', 'DATAMARKER': 'Marker'}, inplace=True)

df_tbl_annual_value['Country'] = df_tbl_annual_value['Physical Flow'].apply(filter_country)
df_tbl_annual_value['Country'] = df_tbl_annual_value['Country'].ffill()
df_tbl_annual_value['Country'] = df_tbl_annual_value['Country'].fillna('United Kingdom')
trace.add_column('Country')
trace.Country('Create Country Value based on country columns in Annual value sheet')
df_tbl_annual_value['ONS Geography Code'] = df_tbl_annual_value['Country'].replace(ons_geography_code_dict)
trace.add_column('ONS Geography Code')
trace.ONS_Geography_Code("Create ONS Geography Code Value based on 'Country' column")
df_tbl_annual_value_country_idx = df_tbl_annual_value[df_tbl_annual_value['Physical Flow'].isin(['England', 'Scotland', 'Wales', 'Northern Ireland'])].index
df_tbl_annual_value.drop(df_tbl_annual_value_country_idx , inplace=True)

df_tbl_annual_value['Period'] = pd.to_numeric(df_tbl_annual_value['Period'], errors='coerce').astype('Int64')
trace.Period("Format 'Period' column to decimal calendar year")

df_tbl_annual_value['Value'] = df_tbl_annual_value.apply(lambda x: None if x['Marker']=='-' else x['Value'], axis=1)
df_tbl_annual_value['Value'] = pd.to_numeric(df_tbl_annual_value['Value'], errors='coerce').astype('float64').replace(np.nan, 'None')
trace.Value("Change - DataMarker to 'None'")
trace.Value("Format 'Value' column to float64 value type")

df_tbl_annual_value['Marker'] = df_tbl_annual_value['Physical Flow']
trace.add_column('Marker')
trace.Marker("Create Marker Value based on 'Physical Flow' column")
df_tbl_annual_value['Unit'] = 'gbp million'
trace.Unit('Hardcoded as gbp million')
df_tbl_annual_value['Measure Type'] = df_tbl_annual_value['Marker']
trace.add_column('Measure Type')
trace.Measure_Type("Create Measure Type Value based on 'Marker' column")

df_tbl_asset_value = trace.combine_and_trace(datasetTitle, 'combined_dataframe_table_asset_value')
trace.add_column('Value')
trace.Value('Rename databaker column OBS to Value')
df_tbl_asset_value.rename(columns={'OBS': 'Value', 'DATAMARKER': 'Marker'}, inplace=True)

df_tbl_asset_value_country_idx = df_tbl_asset_value[df_tbl_asset_value['Marker'].isin(['England', 'Scotland', 'Wales', 'Northern Ireland'])].index
df_tbl_asset_value.drop(df_tbl_asset_value_country_idx , inplace=True)
df_tbl_asset_value['Country'] = df_tbl_asset_value['Country'].fillna('United Kingdom')
trace.add_column('Country')
trace.Country('Create Country Value based on country columns in Asset value sheet')
df_tbl_asset_value['ONS Geography Code'] = df_tbl_asset_value['Country'].replace(ons_geography_code_dict)
trace.add_column('ONS Geography Code')
trace.ONS_Geography_Code("Create ONS Geography Code Value based on 'Country' column")

df_tbl_asset_value['Period'] = pd.to_numeric(df_tbl_asset_value['Period'], errors='coerce').astype('Int64')
trace.Period("Format 'Period' column to decimal calendar year")

df_tbl_asset_value['Value'] = pd.to_numeric(df_tbl_asset_value['Value'], errors='coerce').astype('float64').replace(np.nan, 'None')
trace.Value("Format 'Value' column to float64 value type")

df_tbl_asset_value['Marker'] = df_tbl_asset_value['Physical Flow']
trace.add_column('Marker')
trace.Marker("Create Marker Value based on 'Physical Flow' column")
df_tbl_asset_value['Unit'] = 'gbp million'
trace.Unit('Hardcoded as gbp million')
df_tbl_asset_value['Measure Type'] = df_tbl_asset_value['Marker']
trace.add_column('Measure Type')
trace.Measure_Type("Create Measure Type Value based on 'Marker' column")

df_tbl_physical_flows = df_tbl_physical_flows[['Period', 'Country', 'ONS Geography Code', 'Services', 'Service Type', 'Measure Type', 'Unit', 'Marker', 'Value']]
df_tbl_annual_value = df_tbl_annual_value[['Period', 'Country', 'ONS Geography Code', 'Measure Type', 'Unit',  'Marker', 'Value']]
df_tbl_asset_value = df_tbl_asset_value[['Period', 'Country', 'ONS Geography Code', 'Measure Type', 'Unit', 'Marker', 'Value']]

# Notes from tab
notes = """
Table Physical flows
Sourced from Office for National Statistics - Woodland natural capital accounts \n
Table Annual value
Source by Office for National Statistics \n
Table Asset value
Source from Office for National Statistics
"""
scraper.dataset.comment = notes
scraper.dataset.family = 'climate-change'

# Description from spec
description = """
Scraper Information \n
Methodology
Details of methodologies for woodlands can be found in Woodland natural capital accounts methodology guide, UK: 2020. Further details on the concepts and methodologies underlying the UK natural capital accounts can be found in Principles of Natural Capital Accounting. \n
Strengths and limitations \n
Data quality
The ecosystems services are experimental statistics. Currently, there is no single data source for the UK for the individual ecosystem services. They are calculated from data from the four countries with different timeliness.
Ecosystems provide a diverse range of services and not all have been included in this publication, either owing to unavailability of data or the need for new methods of evaluation. We intend to continue to develop our ability to report on all services.
"""
scraper.dataset.description = scraper.dataset.description + '\n' + description

convert_category_datatype(df_tbl_physical_flows, ['Country', 'ONS Geography Code', 'Services', 'Service Type', 'Marker', 'Measure Type', 'Unit'])
convert_category_datatype(df_tbl_annual_value, ['Country', 'ONS Geography Code', 'Marker', 'Measure Type', 'Unit'])
convert_category_datatype(df_tbl_asset_value, ['Country', 'ONS Geography Code', 'Marker', 'Measure Type', 'Unit'])

pathify_columns(df_tbl_physical_flows, ['Country', 'Services', 'Service Type', 'Marker', 'Measure Type', 'Unit'])
pathify_columns(df_tbl_annual_value, ['Country', 'Marker', 'Measure Type', 'Unit'])
pathify_columns(df_tbl_asset_value, ['Country', 'Marker', 'Measure Type', 'Unit'])

cubes.add_cube(scraper, df_tbl_physical_flows, datasetTitle+'-table-physical-flows')
cubes.add_cube(scraper, df_tbl_annual_value, datasetTitle+'-table-annual-value')
cubes.add_cube(scraper, df_tbl_asset_value, datasetTitle+'-table-asset-value')

cubes.output_all()

trace.render('spec_v1.html')
