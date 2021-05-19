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

for tab in tabs:
    print(tab.name)
