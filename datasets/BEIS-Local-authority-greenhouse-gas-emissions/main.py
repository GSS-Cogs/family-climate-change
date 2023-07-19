import pandas as pd
import numpy as np
from gssutils import *
from csvcubed.models.cube.qb.catalog import CatalogMetadata

df = pd.read_csv("raw.csv")
df.drop(columns=df.columns.values.tolist()[1:5], axis=1, inplace=True)

df.columns.values.tolist()

df.drop(
    columns="CO2 emissions within the scope of influence of LAs (kt CO2e)", inplace=True
)

df.rename(
    columns={
        "Calendar Year": "Year",
        "Greenhouse gas": "Greenhouse Gas",
        "Territorial emissions (kt CO2e)": "Territorial emissions",
        "Mid-year Population (thousands)": "Population",
        "Area (km2)": "Area",
    },
    inplace=True,
)

df["Territorial emissions per capita"] = df["Territorial emissions"] / df["Population"]
df["Territorial emissions per km2 area"] = df["Territorial emissions"] * 1000 / df["Area"]
df.replace([np.inf, -np.inf], 0, inplace=True)
for col in [
    "Territorial emissions",
    "Territorial emissions per capita",
    "Territorial emissions per km2 area",
]:
    df[col] = df[col].astype(str).astype(float).round(4)

df = pd.melt(
    df,
    id_vars=[
        "Country",
        "Local Authority",
        "Local Authority Code",
        "Year",
        "LA GHG Sector",
        "LA GHG Sub-sector",
        "Greenhouse Gas",
    ],
    value_vars=[
        "Territorial emissions",
        "Territorial emissions per capita",
        "Territorial emissions per km2 area",
    ],
    var_name="Measure",
    value_name="Value",
)

df['Value'] = df.apply(lambda x: 0 if np.isnan(
    x['Value']) else x['Value'], axis=1)

df["Unit"] = df.apply(
    lambda x: "kt CO2e"
    if x["Measure"] == "Territorial emissions"
    else "t CO2e"
    if x["Measure"] == "Territorial emissions per capita"
    else "t CO2e"
    if x["Measure"] == "Territorial emissions per km2 area"
    else "",
    axis=1,
)

# Maping for local bespoke country codelist
df["Country"] = (
    df["Country"]
    .replace(
        {
            "England": "E92000001",
            "Wales": "W92000004",
            "Scotland": "S92000003",
            "Northern Ireland": "N92000002"
        }
    )
    .map(
        lambda x: (
            f"http://gss-data.org.uk/data/gss_data/climate-change/beis-local-authority-greenhouse-gas-emissions-concept/country/{pathify(x)}"
            if x == "Unallocated"
            else f"http://statistics.data.gov.uk/id/statistical-geography/{x}"
        )
    )
)

# Maping for local bespoke Local Authority codelist
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

df.drop(columns=["Local Authority", "LA GHG Sector"], inplace=True)
df.rename(
    {"Local Authority Code": "Local Authority", "LA GHG Sub-sector": "Sub Sector"},
    axis=1,
    inplace=True,
)

df["Local Authority"] = df["Local Authority"].map(
    lambda x: (
        f"http://gss-data.org.uk/data/gss_data/climate-change/beis-local-authority-greenhouse-gas-emissions-concept/local-authority/{x}"
        if x in [("large-elec"), ("unallocated-consumption"), ("unallocated-elec-ni")]
        else f"http://statistics.data.gov.uk/id/statistical-geography/{x}"
    )
)

df = df[
    [
        "Year",
        "Country",
        "Local Authority",
        "Sub Sector",
        "Greenhouse Gas",
        "Measure",
        "Unit",
        "Value",
    ]
]

df.to_csv("observations.csv", index=False)

catalog_metadata = CatalogMetadata(
    title="Local authority greenhouse gas emissions",
    summary="UK local authority estimates of greenhouse gas emissions",
    dataset_issued="2023-06-29T09:30:00",
    keywords=[
        "emissions"
        "greenhouse-gas",
        "carbon-dioxide",
        "local-authority",
        "country"
    ],
    license_uri="https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
    public_contact_point_uri="GreenhouseGas.Statistics@energysecurity.gov.uk",
    creator_uri="https://www.gov.uk/government/organisations/department-for-energy-security-and-net-zero",
    publisher_uri="https://www.gov.uk/government/organisations/department-for-energy-security-and-net-zero",
    theme_uris=["http://gss-data.org.uk/def/gdp#climate-change"],
    description="""
    These statistics provide a breakdown of greenhouse gas emissions across the
    UK, using nationally available datasets going back to 2005. This year
    emissions estimates for all sectors and gases span the entire timeseries.
    
    The main data sources are the UK National Atmospheric Emissions Inventory
    and the Department of Energy Security and Net Zero (DESNZ) National
    Statistics of energy consumption for local authority areas. All emissions
    included in the national inventory are covered except those from aviation,
    shipping and military transport, for which there is no obvious basis for
    allocation to local areas, and emissions of fluorinated gases, for which
    suitable data are not available to estimate these emissions at a local level.
    """,
)
catalog_metadata.to_json_file("catalog-metadata.json")