# -*- coding: utf-8 -*-
# # ONS-Woodland-natural-capital-accounts

# +
import pandas as pd
from gssutils import *
import json

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


for tab in tabs:
    print(tab.name)
for tab in tabs:
    print(tab.name)
    if tab.name == 'Physical flows':
        columns = ['Title', 'Period', 'Measure Type' 'Service']
        trace.start(datasetTitle, tab, columns, dist.downloadURL)

        title = tab.excel_ref('A2')
        trace.Title('Defined from cell value: {}', var=cellLoc(title))

        period = tab.excel_ref('C4').expand(RIGHT).is_not_blank()
        trace.Period('Defined from cell range: {}', var=excelRange(period))

        measure_type = tab.excel_ref('B5').expand(DOWN).is_not_blank()
        trace.Measure_Type('Defined from cell range: {}', var=excelRange(measure_type))

        service = tab.excel_ref('A4').expand(DOWN).is_not_blank()
        trace.Service('Defined from cell value: {}', var=cellLoc(service))

        observations = tab.excel_ref('C5').expand(DOWN).expand(RIGHT).is_not_blank()

        dimensions = [
            HDim(title, 'Title', CLOSEST, ABOVE),
            HDim(period, 'Period', DIRECTLY, ABOVE),
            HDim(measure_type, 'Measure Type', DIRECTLY, LEFT),
            HDim(service, 'Service', DIRECTLY, LEFT)
        ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        trace.with_preview(tidy_sheet)
        savepreviewhtml(tidy_sheet, fname=f'{tab.name}_Preview.html')
        trace.store(f'combined_dataframe_table_physical_flows', tidy_sheet.topandas())
