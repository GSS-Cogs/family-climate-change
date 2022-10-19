#!/usr/bin/env python
# coding: utf-8
# %% 
import pandas as pd 
from gssutils import *
from csvcubed.models.cube.qb.catalog import CatalogMetadata

df = pd.read_csv("raw.csv", encoding='ISO-8859-1')

df['GHG generated directly from UK households'] = df['UK Households heating emissions arising from the use of fossil fuels'] + df['UK Transport emissions generated directly by UK households']

df.drop(columns=['UK Households heating emissions arising from the use of fossil fuels', 'UK Transport emissions generated directly by UK households'], axis=1, inplace=True)

df.rename(columns={'GHG from UK produced goods and services consumed by UK residents': 'GHG from UK produced goods and services',
               'GHG embedded in imported goods and services to UK': 'GHG embedded in imported goods and services'
               }, inplace=True) 

df = pd.melt(df, id_vars=['Year'], 
value_vars= ['GHG from UK produced goods and services', 'GHG embedded in imported goods and services', 'GHG generated directly from UK households'], 
var_name='Measure', value_name='Value')

df.to_csv('observations.csv', index=False)
catalog_metadata = CatalogMetadata(
    title = "Greenhouse gas emissions UK consumption",
    summary = "Greenhouse Gas (GHG) emissions associated with UK consumption (UK's carbon footprint)",
    publisher_uri=["https://www.gov.uk/government/organisations/department-for-environment-food-rural-affairs"],
    landing_page_uris=[
        "https://www.gov.uk/government/statistics/uks-carbon-footprint/carbon-footprint-for-the-uk-and-england-to-2019#greenhouse-gas-emissions-associated-with-consumption"],
    description = """
    The carbon footprint refers to emissions that are associated with the consumption
    spending of UK residents on goods and services, wherever in the world these
    emissions arise along the supply chain, and those which are directly generated by
    UK households through private motoring and burning fuel to heat homes.
    These emissions are often referred to as 'consumption emissions' to distinguish them from
    estimates relating to the emissions 'produced' within a country's territory or economic
    sphere. To find out what effect UK consumption has on GHG emissions we
    need to take into account where the goods we buy come from and their associated
    supply chains.
    
    \nSince 1997, the UK economy has continued to move from a manufacturing base towards
    the services sector. One of the consequences of this is that more of the goods we buy
    and use are now produced overseas. This statistical release breaks down emissions
    into: those produced and consumed in the UK; those generated by households
    directly through heating and motoring; and those emissions relating to imports either
    from China, USA, Europe or the Rest of the World. It excludes emissions arising from
    UK produced goods that are exported.
    """
)
catalog_metadata.to_json_file('catalog-metadata.json')

# %%
