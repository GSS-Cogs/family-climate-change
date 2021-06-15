# -*- coding: utf-8 -*-
# # EA-Regulating-for-people-the-environment-and-growth-or-Pollution-Incidents-Data-or-another

# +
import pandas as pd
from gssutils import *
import json
import string
import numpy as np
from dateutil.parser import parse

info = json.load(open('info.json'))
landingPage = info['landingPage']
landingPage

scraper = Scraper(seed='info.json')
scraper

trace = TransformTrace()
cubes = Cubes('info.json')

dist = scraper.distribution(mediaType=ODS, latest=True)
datasetTitle = info['title']
dist
datasetTitle

# The source data is published in ODS format. ODS is converted to xls with the below lines of code as databaker is
# compatible with xls
xls = pd.ExcelFile(dist.downloadURL, engine='odf')
with pd.ExcelWriter('data.xls') as writer:
    for sheet in xls.sheet_names:
        pd.read_excel(xls, sheet).to_excel(writer,sheet, index = False)
    writer.save()
tabs = loadxlstabs('data.xls')

tabs_name = ['Data_for_Publication']
columns=['Event Number', 'Reported Date', 'Incident Operational Area', 'Grid Reference Confirmed', 'EP Incident', 'Impact Level Type',
         'Incident County', 'Incident District', 'Incident Unitary', 'Measure Type', 'Unit']

if len(set(tabs_name)-{x.name for x in tabs}) != 0:
    raise ValueError(f'Aborting. A tab named {set(tabs_name)-{x.name for x in tabs}} required but not found')

tabs = {tab: tab for tab in dist.as_databaker() if tab.name in tabs_name}


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


def convert_category_datatype(df, columns_arr):
    for col in df.columns:
        if col in columns_arr:
            try:
                df[col] = df[col].astype('category').replace(np.nan, 'None')
            except ValueError as err:
                raise ValueError('Failed to convert category data type for column "{}".'.format(col)) from err


def pathify_columns(df, columns_arr):
    for col in df.columns:
        if col in columns_arr:
            try:
                df[col] = df[col].apply(lambda x: pathify(str(x)))
            except Exception as err:
                raise Exception('Failed to pathify column "{}".'.format(col)) from err


# Transform process
for tab in tabs:
    trace.start(datasetTitle, tab, columns, dist.downloadURL)
    print(tab.name)

    event_number = tab.filter('Event No').expand(DOWN).is_not_blank()
    trace.Event_Number('Defined from cell range: {}', var=excelRange(event_number))

    reported_date = tab.filter('Reported Date').expand(DOWN).is_not_blank()
    trace.Reported_Date('Defined from cell range: {}', var=excelRange(reported_date))

    incident_operational_area = tab.filter('Incident Operational Area').expand(DOWN).is_not_blank()
    trace.Incident_Operational_Area('Defined from cell range: {}', var=excelRange(incident_operational_area))

    grid_reference_confirmed = tab.filter('Grid Ref (Confirmed)').expand(DOWN).is_not_blank()
    trace.Grid_Reference_Confirmed('Defined from cell range: {}', var=excelRange(grid_reference_confirmed))

    ep_incident = tab.filter('EP Incident (Y/N)?').expand(DOWN).is_not_blank()
    trace.EP_Incident('Defined from cell range: {}', var=excelRange(ep_incident))

    impact_level_type = tab.filter('Air Env Impact Level').expand(RIGHT).is_not_blank() & tab.filter('Water Env Impact Level').expand(LEFT).is_not_blank()
    trace.Impact_Level_Type('Defined from cell range: {}', var=excelRange(impact_level_type))

    incident_county = tab.filter('Incident County').expand(DOWN).is_not_blank()
    trace.Incident_County('Defined from cell range: {}', var=excelRange(incident_county))

    incident_district = tab.filter('Incident District').expand(DOWN).is_not_blank()
    trace.Incident_District('Defined from cell range: {}', var=excelRange(incident_district))

    incident_unitary = tab.filter('Incident Unitary').expand(DOWN).is_not_blank()
    trace.Incident_Unitary('Defined from cell range: {}', var=excelRange(incident_unitary))

    measure_type = impact_level_type
    trace.Measure_Type('Defined from cell range: {}', var=excelRange(measure_type))

    unit = 'Impact Level'
    trace.Unit('Hardcoded as {}', var=unit)

    observations = tab.filter('Air Env Impact Level').expand(DOWN).expand(RIGHT).is_not_blank() & tab.filter('Water Env Impact Level').expand(DOWN).expand(LEFT).is_not_blank()

    dimensions = [
        HDim(event_number, 'Event Number', DIRECTLY, LEFT),
        HDim(reported_date, 'Reported Date', DIRECTLY, LEFT),
        HDim(incident_operational_area, 'Incident Operational Area', DIRECTLY, LEFT),
        HDim(grid_reference_confirmed, 'Grid Reference Confirmed', DIRECTLY, LEFT),
        HDim(ep_incident, 'EP Incident', DIRECTLY, LEFT),
        HDim(impact_level_type, 'Impact Level Type', DIRECTLY, ABOVE),
        HDim(incident_county, 'Incident County', DIRECTLY, RIGHT),
        HDim(incident_district, 'Incident District', DIRECTLY, RIGHT),
        HDim(incident_unitary, 'Incident Unitary', DIRECTLY, RIGHT),
        HDim(measure_type, 'Measure Type', DIRECTLY, ABOVE),
        HDimConst('Unit', unit)
    ]

    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    trace.with_preview(tidy_sheet)
    savepreviewhtml(tidy_sheet, fname=f'{tab.name}_Preview.html')
    trace.store(f'combined_dataframe', tidy_sheet.topandas())

# Notes from tab
notes = """
Data limitations
It does not include incidents relating to:
Fisheries incidents – incidents involving illegal fishing and illegal fish movements, fish disease, fishery management activities and fish kills from non-pollution causes, including low flows and low dissolved oxygen.
Water Resources incidents – incidents involving the quantity of a water resource.
Waterways incidents – incidents on a waterway where we are the competent authority for navigation. 
Flood and Coastal Risk Management incidents – for incidents which involve actual or potential flooding and land drainage works. 
Only incidents where our investigations and response have been completed are included.  Some incidents may take an extended period of months, or exceptionally years, to be completed.
The dataset only includes substantiated incidents and their environmental impact. These are where we have confirmation that the incident took place either by a visit from us or a partner organisation, or it is corroborated by other information.
"""
scraper.dataset.comment = notes
scraper.dataset.family = 'climate-change'

description = """
This data is a snapshot taken in August 2020 for the calendar year 2019. We've made it available to members of the public for information. \n
We've published data under the Environment Agency conditional licence \n
If you use the information, you must meet the conditions of the licence. \n
The latest environmental pollution incidents dataset is available on data.gov.uk \n
If you need more current data, please contact the Environment Agency
"""
scraper.dataset.description = scraper.dataset.description + '\n' + description

df = trace.combine_and_trace(datasetTitle, 'combined_dataframe')
trace.add_column('Value')
trace.Value('Rename databaker column OBS to Value')
df.rename(columns={'OBS': 'Value', 'DATAMARKER': 'Marker'}, inplace=True)
df_marker_idx = df[df['Marker'].isin(['Air Env Impact Level', 'Land Env Impact Level', 'Water Env Impact Level'])].index
df.drop(df_marker_idx , inplace=True)

df['Event Number'] = pd.to_numeric(df['Event Number'], errors='coerce').astype('Int64')

df['Reported Date'] = df['Reported Date'].apply(lambda x: parse(str(x)).strftime('%Y-%m-%dT%H:%M:%S'))
trace.Reported_Date("Format 'Reported Date' with gregorian day format")

df['Value'] = df['Marker']
trace.Value("Create Value based on 'Marker' column")

df = df[['Event Number', 'Reported Date', 'Incident Operational Area', 'Grid Reference Confirmed', 'EP Incident', 'Impact Level Type', 'Incident County', 'Incident District', 'Incident Unitary', 'Measure Type', 'Unit', 'Marker', 'Value']]

convert_category_datatype(df, ['Incident Operational Area', 'Grid Reference Confirmed', 'EP Incident', 'Impact Level Type', 'Incident County', 'Incident District', 'Incident Unitary', 'Measure Type', 'Unit', 'Marker', 'Value'])

pathify_columns(df, ['Incident Operational Area', 'Grid Reference Confirmed', 'EP Incident', 'Impact Level Type', 'Incident County', 'Incident District', 'Incident Unitary', 'Measure Type', 'Unit', 'Marker', 'Value'])

trace.Grid_Reference_Confirmed("Rename 'Grid Reference Confirmed' column to 'Grid Reference (Confirmed)'")
trace.EP_Incident("Rename 'EP Incident' column to 'EP Incident (Y/N)?'")
df.rename(columns = {'Grid Reference Confirmed': 'Grid Reference (Confirmed)', 'EP Incident': 'EP Incident (Y/N)?'}, inplace = True)

cubes.add_cube(scraper, df, datasetTitle)

cubes.output_all()

trace.render('spec_v1.html')
