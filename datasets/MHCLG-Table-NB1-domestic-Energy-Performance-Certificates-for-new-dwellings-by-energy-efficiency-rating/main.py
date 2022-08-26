from gssutils import *
import json
import pandas as pd
import numpy as np

def get_distribution(info_json):
    """
    Gets distribution from landing page using info.json based on title of the sheet
    """
    metadata = Scraper(seed=info_json)
    distribution = metadata.distribution(title = lambda x: "Table NB1" in x)
    return  distribution

def get_metadata(info_json):
    """
    Obtain metadata using info.json
    """
    metadata = Scraper(seed=info_json)
    return metadata

def get_title_id(info_json):
    """
    Gets title id from info.json
    """
    info = json.load(open(info_json))
    title_id = info['id']
    return title_id

def dataframe_from_excel_or_ods(distro, sheet_name, header):
    """
    With the help of distribution, sheets are converted to one single dataframe
    """
    all_df = pd.read_excel(distro.downloadURL, sheet_name, header)
    dict_values = all_df.values()
    every_list = [x for x in dict_values]

    for dict_key in all_df.keys():
        if dict_key == "NB1":
            df1 = pd.DataFrame(every_list[0])
            df1["Location"] = "England and Wales"

        elif dict_key == "NB1_England_Only":
            df2 = pd.DataFrame(every_list[1])
            df2["Location"] = "http://statistics.data.gov.uk/id/statistical-geography/E92000001"

        elif dict_key == "NB1_Wales_Only":
            df3 = pd.DataFrame(every_list[2])
            df3["Location"] = "http://data.europa.eu/nuts/code/UKL"

            df4 = pd.concat([df1, df2, df3])
 
            df4.drop(df4.loc[df4["Year"] == "Total"].index, inplace = True)
            df4 = df4[~df4["Year"].isin(["Total"])]
 
            df4.Quarter.fillna(df4.Year, inplace = True)
            del df4["Year"]
 
            df4["Not Recorded"] = df4["Not Recorded"].fillna(df4.pop("Not  Recorded"))
            df4.rename(columns = {"Quarter":"Period", "Number of Lodgements":"Lodgements"}, inplace = True)

        elif dict_key == "NB1_By_Region":
            df5 = pd.DataFrame(every_list[3])
            df5 = df5.drop(df5.index[0:10])
            df5.rename(columns = {"Region":"Location", "Number of Lodgements":"Lodgements", "Quarter":"Period"}, inplace = True)

        elif dict_key == "NB1_By_LA":
            df6 = pd.DataFrame(every_list[4])
            df6 = df6.drop(["Local Authority"], axis = 1)
            df6.rename(columns = {"Local Authority Code":"Location", "Number of Lodgements":"Lodgements", "Quarter":"Period"}, inplace = True)

            df7 = pd.concat([df4, df5, df6]).fillna('')
            return df7

def melting_dataframe(data_frame):
    """
    The dataframe is melted from wide to long format
    """
    tidy_df = pd.melt(data_frame, id_vars = ['Period', 'Lodgements', 'Total Floor Area (m2)', 'Location'], value_vars = ['A', 'B',
           'C', 'D', 'E', 'F', 'G', 'Not Recorded'], var_name = "Efficieny Rating", ignore_index=False)
    return tidy_df

def postprocessing_the_dataframe(tidy):
    """
    Formatting the date column and post processing the dataframe
    """
    tidy = tidy[~tidy["Period"].isin(["Total"])]
    tidy["Period"] =  tidy["Period"].astype(str).apply(lambda x: "year/" + x[:4] if len(x) == 4 else "quarter/" + x[:4] + "-0" + x[5:6] if len(x) == 6 else '')
    tidy.rename(columns = {"value":"Value"}, inplace = True)
    tidy = tidy.replace({'Location': {
    "East Midlands": "http://data.europa.eu/nuts/code/UKF",
    "London": "http://data.europa.eu/nuts/code/UKI",
    "North East": "http://data.europa.eu/nuts/code/UKC",
    "North West": "http://data.europa.eu/nuts/code/UKD",
    "South East": "http://data.europa.eu/nuts/code/UKJ",
    "South West": "http://data.europa.eu/nuts/code/UKK",
    "East of England": "http://data.europa.eu/nuts/code/UKH",
    "West Midlands": "http://data.europa.eu/nuts/code/UKG",
    "Yorkshire and The Humber": "http://data.europa.eu/nuts/code/UKE",
    "Unknown": 'http://gss-data.org.uk/data/gss_data/climate-change/' +
    title_id + '#concept/local-authority-code/unknown',
    "England and Wales" : 'http://gss-data.org.uk/data/gss_data/climate-change/' +
    title_id + '#concept/local-authority-code/england-wales'
    }})
    sic = 'http://statistics.data.gov.uk/id/statistical-geography/'
    tidy['Location'] = tidy['Location'].map(
    lambda x: sic + x if 'E0' in x else (  sic + x if 'W0' in x else x))
    tidy = tidy.replace({'Efficieny Rating': {
    "Not recorded": "Not Recorded",
    "not-recorded": 'Not Recorded'
    }})
    tidy['Measure Type'] = 'energy-performance-certificates'
    tidy['Unit'] = 'Count'
    df = tidy[['Period', 'Lodgements', 'Total Floor Area (m2)', 'Location',
       'Efficieny Rating', 'Value', 'Measure Type', 'Unit']]
    return df


if __name__ == "__main__":
    distribution = get_distribution("info.json")
    metadata = get_metadata("info.json")
    title_id = get_title_id("info.json")
    df7 = dataframe_from_excel_or_ods(distro = distribution, sheet_name = ["NB1", "NB1_England_Only", "NB1_Wales_Only", "NB1_By_Region", "NB1_By_LA"], header = 3)
    tidy_df = melting_dataframe(data_frame = df7)
    df = postprocessing_the_dataframe(tidy = tidy_df)

    df.to_csv('observations.csv', index=False)
    catalog_metadata = metadata.as_csvqb_catalog_metadata()
    catalog_metadata.to_json_file('catalog-metadata.json')