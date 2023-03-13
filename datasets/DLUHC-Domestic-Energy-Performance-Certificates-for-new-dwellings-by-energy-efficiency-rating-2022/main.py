from gssutils import *
import json
import pandas as pd
import numpy as np

class StageOne:
    """
    Distribution, metadata and title_id is extracted
    """
    def __init__(self, info_json):
        self.info_json = info_json

    def get_distribution(self):
        """
        Gets distribution from landing page using info.json based on title of the sheet
        """
        metadata = Scraper(seed=self.info_json)
        return  metadata.distribution(title = lambda x: "Table NB1: domestic Energy Performance Certificates for new dwellings by energy efficiency rating" in x)

    @staticmethod
    def get_metadata(info_json):
        """
        Obtain metadata using info.json
        """
        metadata = Scraper(seed=info_json)
        return metadata

    @staticmethod
    def get_title_id(info_json):
        """
        Gets title id from info.json
        """
        info = json.load(open(info_json))
        title_id = info['id']
        return title_id
class SpecificSheet:
    """
    Name of the sheets to be transformed is validated
    """
    def __init__(self, download_the_sheet):
        self.download_the_sheet = download_the_sheet

    def get_specific_dataset(self):
        """
        Extracts specific raw dataset to be transformed
        """
        return self.download_the_sheet

    def get_all_sheet_name(self):
        """
        Extract all the sheet names from specific raw dataset
        """
        xl = pd.ExcelFile(self.download_the_sheet)
        # xl.parse("NB1")  # read a specific sheet to DataFrame
        sheet_names = xl.sheet_names
        return sheet_names

    def sheets_to_transform(self):
        """
        Extract sheet names to be transformed and validated
        """
        sheets_to_transform = [sheet for sheet in all_sheets if sheet.startswith("NB1")]
        if len(set(sheets_to_transform)-set(all_sheets)) != 0:
            raise ValueError(f'Aborting. A tab named  {set(sheets_to_transform)-set(all_sheets)} required but not found')
        else:
            return sheets_to_transform
        
class TransformationStageOne:

    """
    Raw data is transformed into tidy data and melted
    """

    def __init__(self, distro, sheet_name, header):
        self.distro = distro
        self.sheet_name = sheet_name
        self.header = header

    def dataframe_from_excel_or_ods(self):
        """
        With the help of distribution, sheets are converted to one single dataframe
        """
        all_df = pd.read_excel(self.distro.downloadURL, self.sheet_name, self.header)
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
    
    def melting_dataframe(self):
        """
        The dataframe is melted from wide to long format
        """
        tidy_df = pd.melt(df7, id_vars = ['Period', 'Lodgements', 'Total Floor Area (m2)', 'Location'], value_vars = ['A', 'B',
            'C', 'D', 'E', 'F', 'G', 'Not Recorded'], var_name = "Efficieny Rating", ignore_index=False)
        return tidy_df
    
class PostProcessing:

    """
    Transformed tidy data is postprocessed and valid duplicates are dropped
    """

    def __init__(self, tidy, title_id):
        self.tidy = tidy
        self.title_id = title_id

    def postprocessing_the_dataframe(self):
        """
        Formatting the date column and post processing the dataframe
        """
        self.tidy["Period"] =  self.tidy["Period"].astype(str).apply(lambda x: "year/" + x[:4] if len(x) == 4 else "quarter/" + x[:4] + "-0" + x[5:6] if len(x) == 6 else '')

        self.tidy = self.tidy[~self.tidy["Period"].isin(["Total"])]
        self.tidy.rename(columns = {"value":"Value"}, inplace = True)
        self.tidy['Measure Type'] = 'energy-performance-certificates'
        self.tidy['Unit'] = 'Count'

        self.tidy = self.tidy.replace({'Location': {
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
        self.tidy['Location'] = self.tidy['Location'].map(
        lambda x: sic + x if 'E0' in x else (  sic + x if 'W0' in x else x))

        df = self.tidy[['Period', 'Lodgements', 'Total Floor Area (m2)', 'Location',
        'Efficieny Rating', 'Value', 'Measure Type', 'Unit']]

        #valid to drop
        df = df.drop_duplicates()

        return df

    
if __name__ == "__main__":

    my_distribution = StageOne(info_json="info.json")
    distribution = my_distribution.get_distribution()
    metadata = my_distribution.get_metadata(info_json="info.json")
    title_id = my_distribution.get_title_id(info_json="info.json")

    specific_sheet = SpecificSheet(distribution.downloadURL)
    dataset = specific_sheet.get_specific_dataset()
    all_sheets = specific_sheet.get_all_sheet_name()
    sheet_name = specific_sheet.sheets_to_transform()

    dataframe = TransformationStageOne(distro = distribution, sheet_name = sheet_name, header = 3)
    df7 = dataframe.dataframe_from_excel_or_ods()
    tidy = dataframe.melting_dataframe()

    clean_df = PostProcessing(tidy, title_id)
    df = clean_df.postprocessing_the_dataframe()
    # print(df.head(5))