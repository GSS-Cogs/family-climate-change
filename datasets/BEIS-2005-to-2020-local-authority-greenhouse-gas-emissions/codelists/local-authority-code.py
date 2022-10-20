import json
import pandas as pd
from gssutils import Cubes, Scraper, pathify

metadata = Scraper(seed='../info.json')
distribution = metadata.distribution(mediaType='text/csv')
metadata.dataset.title = distribution.title

df = (
    distribution
    .as_pandas()
    .assign(**{"Local Authority Code": lambda df: df["Local Authority Code"].combine_first(df["Local Authority"])})
)

g = pd.DataFrame()

g["Label"] = df["Local Authority Code"].unique()
g["URI"] = (
    g["Label"]
    .replace({
        "Unallocated consumption": pathify("Unallocated consumption"),
        "Large elec users (high voltage lines) unknown location": pathify("Large elec users (high voltage lines) unknown location")
    })
    .map(lambda x: (
        f"http://gss-data.org.uk/data/gss_data/climate-change/beis-2005-to-2019-local-authority-carbon-dioxide-co2-emissions#concept/local-authority-code/{x}" if x in [
            pathify("Unallocated consumption"), 
            pathify("Large elec users (high voltage lines) unknown location")
        ] else f"http://statistics.data.gov.uk/id/statistical-geography/{x}"
    ))
)
g["Parent URI"] = None
g["Sort Priority"] = g.index
g["Description"] = None
g["Local Notation"] = g["Label"].replace({
    "Unallocated consumption": pathify("Unallocated consumption"),
    "Large elec users (high voltage lines) unknown location": pathify("Large elec users (high voltage lines) unknown location")
})

g.to_csv("./local-authority-code.csv", index=False)