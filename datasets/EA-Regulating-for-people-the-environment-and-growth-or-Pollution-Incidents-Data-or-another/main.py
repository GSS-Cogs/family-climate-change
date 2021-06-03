# -*- coding: utf-8 -*-
# # EA-Regulating-for-people-the-environment-and-growth-or-Pollution-Incidents-Data-or-another

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
