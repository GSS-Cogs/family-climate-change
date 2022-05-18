# +
import json
import pandas as pd
from gssutils import *

metadata = Scraper(seed="info.json")
metadata
# -
distribution = metadata.distribution(latest = True)
distribution

tabs = {tab.name: tab for tab in metadata.distribution(latest = True).as_databaker()}

list(tabs)

tidied_sheets = []
for name, tab in tabs.items():
    if 'Cover_sheet' in name or 'Notes' in name:
        continue
    print(tab.name)


    unwanted = tab.filter(contains_string("Which of the following"))

    unwanted_columns = tab.filter(contains_string("Table 1a: Estimates")).fill(DOWN).one_of(["Survey question and response options", 
                                                                                            "Table 1c: Associated weighted counts and sample sizes", 
                                                                                            "Survey question"]) | unwanted

    percentage_estimates_by_age = tab.filter(contains_string("Survey question")).fill(RIGHT).is_not_blank().is_not_whitespace()

    impact_parameters = tab.filter(contains_string("Survey question")).fill(DOWN).is_not_blank().is_not_whitespace() - unwanted_columns

    observations = impact_parameters.fill(RIGHT).is_not_blank().is_not_whitespace()


    dimensions = [
        HDim(percentage_estimates_by_age, "Percentage Estimates By Age", DIRECTLY, ABOVE),
        HDim(impact_parameters, "Impact Parameters", DIRECTLY, LEFT)
    ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    tidied_sheets.append(tidy_sheet.topandas())
    

df = pd.concat(tidied_sheets, sort = True)

df

df["Impact Parameters"].unique()

df["Percentage Estimates By Age"].unique()

df["Percentage Estimates By Age"] = df["Percentage Estimates By Age"].map(lambda x: x.rstrip('\n% ')).replace(r'\n', '', regex = True)

df["Percentage Estimates By Age"].unique()

df['Confidence Intervals'] = 'not-applicable'

df

df["Confidence Intervals"] = df.apply(lambda x: "AllpersonsLCL" if x["Percentage Estimates By Age"] == "AllpersonsLCL"
                                else "All personsUCL" if x["Percentage Estimates By Age"] == "All personsUCL"
                                else "Aged 16 to 29LCL" if x["Percentage Estimates By Age"] == "Aged 16 to 29LCL"
                                else "Aged16 to 29UCL" if x["Percentage Estimates By Age"] == "Aged16 to 29UCL"
                                else "Aged30 to 49LCL" if x["Percentage Estimates By Age"] == "Aged30 to 49LCL"
                                else "Aged30 to 49UCL" if x["Percentage Estimates By Age"] == "Aged30 to 49UCL"
                                else "Aged50 to 69LCL" if x["Percentage Estimates By Age"] == "Aged50 to 69LCL"
                                else "Aged50 to 69UCL" if x["Percentage Estimates By Age"] == "Aged50 to 69UCL"
                                else "Aged 70 and over LCL" if x["Percentage Estimates By Age"] == "Aged 70 and over LCL"
                                else "Aged 70 and overUCL" if x["Percentage Estimates By Age"] == "Aged 70 and overUCL" 
                                else "Aged 16 to 49 LCL" if x["Percentage Estimates By Age"] == "Aged 16 to 49 LCL"
                                else "Aged 16 to 49 UCL" if x["Percentage Estimates By Age"] == "Aged 16 to 49 UCL"
                                else "Aged50 and overLCL" if x["Percentage Estimates By Age"] == "Aged50 and overLCL"
                                else "Aged50 and overUCL" if x["Percentage Estimates By Age"] == "Aged50 and overUCL"
                                else "Men LCL" if x["Percentage Estimates By Age"] == "Men LCL"
                                else "Men UCL" if x["Percentage Estimates By Age"] == "Men UCL"
                                else "Women LCL" if x["Percentage Estimates By Age"] == "Women LCL"
                                else "Women UCL" if x["Percentage Estimates By Age"] == "Women UCL"
                                else x["Confidence Intervals"], axis = 1)

df

df["Confidence Intervals"].unique()

values_to_drop = ['AllpersonsLCL', 'All personsUCL', 'Aged 16 to 29LCL',
       'Aged16 to 29UCL', 'Aged30 to 49LCL', 'Aged30 to 49UCL',
       'Aged50 to 69LCL', 'Aged50 to 69UCL', 'Aged 70 and over LCL',
       'Aged 70 and overUCL', 'Aged 16 to 49 LCL', 'Aged 16 to 49 UCL',
       'Aged50 and overLCL', 'Aged50 and overUCL', 'Men LCL', 'Men UCL',
       'Women LCL', 'Women UCL']

df["Percentage Estimates By Age"] = df.apply(lambda x: "not-applicable" if x["Confidence Intervals"] in values_to_drop else x["Percentage Estimates By Age"], axis = 1) 

df["Percentage Estimates By Age"].unique()

df["Confidence Intervals"].unique()

df.columns

df[['Percentage Estimates By Age','Confidence Intervals','Impact Parameters', 'OBS']]

df

df.rename(columns = {'OBS' : 'Value'}, inplace = True)

df.to_csv("observations.csv", index = False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')


