from gssutils import *
import json
import pandas as pd
import numpy as np

def distribution_and_title_id(info_json):
    metadata = Scraper(seed=info_json)
    distribution = metadata.distribution(title = lambda x: "Table NB1" in x)
    return  distribution

def title_id(info_json):
    info = json.load(open(info_json))
    title_id = info['id']
    return title_id

d1 = distribution_and_title_id("info.json")
t1 = title_id("info.json")

def dataframe_from_excel_or_ods(distro, sheet_name, header):
    if sheet_name == "NB1" or "NB1_England_Only" or "NB1_Wales_Only" or "NB1_By_Region" or "NB1_By_LA":
        df = pd.read_excel(distro.downloadURL, sheet_name, header)

    if sheet_name == "NB1" or "NB1_England_Only" or "NB1_Wales_Only":
        multi_lists = df.values()
        every_list = [x for x in multi_lists]

        df1 = pd.DataFrame(every_list[0])
        df1["Location"] = "England and Wales"

        df2 = pd.DataFrame(every_list[1])
        df2["Location"] = "http://statistics.data.gov.uk/id/statistical-geography/E92000001"

        df3 = pd.DataFrame(every_list[2])
        df3["Location"] = "http://data.europa.eu/nuts/code/UKL"

        df4 = pd.concat([df1, df2, df3])

        df4.drop(df4.loc[df4["Year"] == "Total"].index, inplace = True)
        df4 = df4[~df4["Year"].isin(["Total"])]

        df4.Quarter.fillna(df4.Year, inplace = True)
        del df4["Year"]

        df4["Not Recorded"] = df4["Not Recorded"].fillna(df4.pop("Not  Recorded"))

        frame1 = pd.melt(df, id_vars = ['Quarter', 'Number of Lodgements', 'Total Floor Area (m2)', 'location'], value_vars = ['A', 'B',
       'C', 'D', 'E', 'F', 'G', 'Not Recorded'], var_name = "Efficieny Rating", ignore_index=False)

    if sheet_name == "NB1_By_Region":
        df5 = df.drop(df.index[0:10])




dataframe_from_excel_or_ods(distro = d1, sheet_name = ["NB1_By_Region"], header = 3)