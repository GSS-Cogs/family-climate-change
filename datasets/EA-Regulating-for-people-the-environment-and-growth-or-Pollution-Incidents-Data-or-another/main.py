# -*- coding: utf-8 -*-
# # EA-Regulating-for-people-the-environment-and-growth-or-Pollution-Incidents-Data-or-another

# +
import pandas as pd
from gssutils import *
import json
import string

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
columns=['Event No', 'Reported Date', 'Incident Operational Area', 'Grid Ref Confirmed', 'EP Incident', 'Impact Level',
         'Incident County', 'Incident District', 'Incident Unitary']

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


# Transform process
for tab in tabs:
    trace.start(datasetTitle, tab, columns, dist.downloadURL)
    print(tab.name)

    event_no = tab.filter('Event No').expand(DOWN).is_not_blank()
    trace.Event_No('Defined from cell range: {}', var=excelRange(event_no))

    reported_date = tab.filter('Reported Date').expand(DOWN).is_not_blank()
    trace.Reported_Date('Defined from cell range: {}', var=excelRange(reported_date))

