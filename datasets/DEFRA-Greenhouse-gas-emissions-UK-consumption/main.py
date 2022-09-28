#!/usr/bin/env python
# coding: utf-8
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
    summary = "The UK's total carbon footprint",
    description = "Final estimates consumption of UK greenhouse gas emissions."
)
catalog_metadata.to_json_file('catalog-metadata.json')
