import json
import pandas as pd
import numpy as np
from gssutils import *

metadata = Scraper(seed='info.json')
metadata

distribution = metadata.distribution(latest = True, mediaType = "text/csv",
                                        title = lambda x: x.endswith("2005 to 2020 local authority greenhouse gas emissions dataset"))
distribution

df = distribution.as_pandas()
df.head(5)
df.tail(5)