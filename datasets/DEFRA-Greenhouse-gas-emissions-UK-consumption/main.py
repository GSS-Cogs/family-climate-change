#!/usr/bin/env python
# coding: utf-8
import pandas as pd 
from gssutils import *
from csvcubed.models.cube.qb.catalog import CatalogMetadata

df = pd.read_csv("raw.csv", encoding='ISO-8859-1')

df.rename(columns={'GHG from UK produced goods and services consumed by UK residents': 'GHG from UK produced goods and services',
               'GHG embedded in imported goods and services to UK': 'GHG embedded in imported goods and services',
               'UK Households heating emissions arising from the use of fossil fuels': 'GHG generated by UK households from fossil fuels',
               'UK Transport emissions generated directly by UK households': 'GHG generated by UK households directly from transport'
               }, inplace=True) 

df = pd.melt(df, id_vars=['Year'], 
value_vars= ['GHG from UK produced goods and services', 'GHG embedded in imported goods and services', 'GHG generated by UK households from fossil fuels', 'GHG generated by UK households directly from transport'], 
var_name='Measure', value_name='Value')

df.to_csv('observations.csv', index=False)
catalog_metadata = CatalogMetadata(
    title = "Greenhouse gas emissions UK consumption",
    description = "Final estimates consumption of UK greenhouse gas emissions. Loaded to Airtable at the request of DE (Osamede)."
)
catalog_metadata.to_json_file('catalog-metadata.json')
