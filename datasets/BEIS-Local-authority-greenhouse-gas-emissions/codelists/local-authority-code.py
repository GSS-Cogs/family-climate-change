import pandas as pd
import numpy as np
from gssutils import *
from csvcubed.models.cube.qb.catalog import CatalogMetadata

df = pd.read_csv("local-authority-ghg-emissions.csv")

g = pd.DataFrame()

g["Label"] = df["Local Authority Code"].unique()
g["URI"] = (
    g["Label"]
    .replace({
        "Unallocated consumption": pathify("Unallocated consumption"),
        "Large elec users (high voltage lines) unknown location": pathify("Large elec users (high voltage lines) unknown location")
    })
    .map(lambda x: (
        f"http://gss-data.org.uk/data/gss_data/climate-change/beis-2005-to-2021-local-authority-carbon-dioxide-co2-emissions#concept/local-authority-code/{x}" if x in [
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