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

# ## DEFRA-B3-State-of-the-water-environment

import json
import pandas as pandas
from gssutils import *

cubes = Cubes('info.json')
info = json.load(open('info.json'))
landingPage = info['landingPage']
landingPage

metadata = Scraper(seed="info.json")
metadata

distribution = metadata.distribution(mediaType="text/csv")
distribution

df = distribution.as_pandas()
