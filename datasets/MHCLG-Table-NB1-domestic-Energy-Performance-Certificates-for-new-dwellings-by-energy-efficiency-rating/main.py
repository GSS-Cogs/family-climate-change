from gssutils import *
import json
import pandas as pd
import numpy as np

def distribution_and_title_id(info_json):
    metadata = Scraper(seed=info_json)
    distribution = metadata.distribution(title = lambda x: "Table NB1" in x)
    return  distribution

def get_metadata(info_json):
    metadata = Scraper(seed=info_json)
    return metadata

def title_id(info_json):
    info = json.load(open("info.json"))
    title_id = info['id']
    return title_id

def dataframe_from_excel_or_ods(distro, sheet_name, header):
    if sheet_name == "NB1" or "NB1_England_Only" or "NB1_Wales_Only" or "NB1_By_Region" or "NB1_By_LA":
        df = pd.read_excel(distro.downloadURL, sheet_name, header)
        # return df

        if sheet_name == ["NB1", "NB1_England_Only", "NB1_Wales_Only"]:
            dict_values = df.values()
            every_list = [x for x in dict_values]
 
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
            df4.rename(columns = {"Quarter":"Period", "Number of Lodgements":"Lodgements"}, inplace = True)
            return df4
        
        if sheet_name == ["NB1_By_Region"]:
            second_dict_values = df.values()
            second_list = [x for x in second_dict_values]

            df5 = pd.DataFrame(second_list[0])
            df5 = df5.drop(df5.index[0:10])
 
            df5.rename(columns = {"Region":"Location", "Number of Lodgements":"Lodgements", "Quarter":"Period"}, inplace = True)
            return df5

        if sheet_name == ["NB1_By_LA"]:
            third_dict_values = df.values()
            third_list = [x for x in third_dict_values]

            df6 = pd.DataFrame(third_list[0])
            df6 = df6.drop(["Local Authority"], axis = 1)
 
            df6.rename(columns = {"Local Authority Code":"Location", "Number of Lodgements":"Lodgements", "Quarter":"Period"}, inplace = True)
            return df6

def melting_multiple_dataframes(data_frame):
    frames = pd.melt(data_frame, id_vars = ['Period', 'Lodgements', 'Total Floor Area (m2)', 'Location'], value_vars = ['A', 'B',
           'C', 'D', 'E', 'F', 'G', 'Not Recorded'], var_name = "Efficieny Rating", ignore_index=False)
    return frames

def combining_frames_postprocessing(multiple_frames):
    # return multiple_frames, type(multiple_frames)
    tidy = pd.concat(multiple_frames).fillna('')
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
    t1 + '#concept/local-authority-code/unknown',
    "England and Wales" : 'http://gss-data.org.uk/data/gss_data/climate-change/' +
    t1 + '#concept/local-authority-code/england-wales'
    }})
    sic = 'http://statistics.data.gov.uk/id/statistical-geography/'
    tidy['Location'] = tidy['Location'].map(
    lambda x: sic + x if 'E0' in x else (  sic + x if 'W0' in x else x))
    tidy = tidy.replace({'Efficieny Rating': {
    "Not recorded": "Not Recorded",
    "not-recorded": 'Not Recorded'
    }})
    tidy['Measure Type'] = 'energy-performance-certificates'
    tidy['Unit'] = 'count'
    tidy = tidy[['Period', 'Lodgements', 'Total Floor Area (m2)', 'Location',
       'Efficieny Rating', 'Value', 'Measure Type', 'Unit']]
    tidy = tidy[['Period', 'Lodgements', 'Total Floor Area (m2)', 'Location',
       'Efficieny Rating', 'Value', 'Measure Type', 'Unit']]
    return tidy

if __name__ == "__main__":
    d1 = distribution_and_title_id("info.json")
    m1 = get_metadata("info.json")
    t1 = title_id("info.json")
    nb1 = dataframe_from_excel_or_ods(distro = d1, sheet_name = ["NB1", "NB1_England_Only", "NB1_Wales_Only"], header = 3)
    nb1_region = dataframe_from_excel_or_ods(distro = d1, sheet_name = ["NB1_By_Region"], header = 3)
    nb1_la = dataframe_from_excel_or_ods(distro = d1, sheet_name = ["NB1_By_LA"], header = 3)
    frame1 = melting_multiple_dataframes(nb1)
    frame2 = melting_multiple_dataframes(nb1_region)
    frame3 = melting_multiple_dataframes(nb1_la)
    tidy = combining_frames_postprocessing([frame1, frame2, frame3])
    
    tidy.to_csv('observations.csv', index=False)
    catalog_metadata = m1.as_csvqb_catalog_metadata()
    catalog_metadata.to_json_file('catalog-metadata.json')