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
