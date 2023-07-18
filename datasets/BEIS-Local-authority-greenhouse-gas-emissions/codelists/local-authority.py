import json
import pandas as pd
from gssutils import Cubes, Scraper, pathify

df = pd.read_csv("../raw.csv")
df.drop(columns=df.columns.values.tolist()[1:5], axis=1, inplace=True)

df["Local Authority Code"] = df.apply(
    lambda x: "unallocated-elec-ni"
    if x["Local Authority"] == "Unallocated electricity NI"
    else "unallocated-consumption"
    if x["Local Authority"] == "Unallocated consumption"
    else "large-elec"
    if x["Local Authority"] == "Large elec users (high voltage lines) unknown location"
    else x["Local Authority Code"],
    axis=1,
)

df = (df
    .assign(**{"Local Authority Code": lambda df: df["Local Authority Code"].combine_first(df["Local Authority"])})
)

g = pd.DataFrame()

g["Label"] = df["Local Authority"].unique()
g["Label"].replace({"Large elec users (high voltage lines) unknown location": "Large electricity users (high voltage lines) unknown location"}, inplace=True)

g['Notation'] = df["Local Authority Code"].unique()

#  Maping for local bespoke codelist for Local Authority code with URI 
g["URI"] = g['Notation'].map(
    lambda x: (
        f"http://gss-data.org.uk/data/gss_data/climate-change/beis-local-authority-greenhouse-gas-emissions#concept/local-authority/{x}"
        if x in [("large-elec"), ("unallocated-consumption"), ("unallocated-elec-ni")]
        else f"http://statistics.data.gov.uk/id/statistical-geography/{x}"
    )
)

g["Parent URI"] = None
g.index += 1
g["Sort Priority"] = g.index
g["Description"] = None

g["Local Notation"] = g['Notation']
g.drop(columns='Notation', inplace=True)
g.to_csv("./local-authority.csv", index=False)