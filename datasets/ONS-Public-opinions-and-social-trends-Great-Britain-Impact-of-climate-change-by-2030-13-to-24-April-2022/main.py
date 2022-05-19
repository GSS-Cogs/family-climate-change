# +
import json
import pandas as pd
from gssutils import *

metadata = Scraper(seed="info.json")
metadata
# -
distribution = metadata.distribution(latest = True, 
                mediaType = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
                title = lambda x: "Impact of climate change by 2030 - 2022-05-12" )
distribution

tabs = distribution.as_databaker()

tabs = [tab for tab in tabs if tab.name not in ['Cover_sheet', 'Notes']]

tidied_sheets = []
tabs = [tab for tab in tabs if tab.name not in ['Cover_sheet', 'Notes']]
for tab in tabs:

    print(tab.name)

    anchor = tab.excel_ref("A1")

    unwanted = tab.filter(contains_string("Which of the following"))

    unwanted_columns = tab.filter(contains_string("None of these")).fill(DOWN)

    percentage_estimates_by_age = tab.filter(contains_string("Survey question and response options")).fill(RIGHT).is_not_blank().is_not_whitespace()

    impact_parameters = tab.filter(contains_string("Survey question and response options")).fill(DOWN).is_not_blank().is_not_whitespace() - unwanted_columns

    observations = impact_parameters.fill(RIGHT).is_not_blank().is_not_whitespace()


    dimensions = [
        HDim(percentage_estimates_by_age, "Percentage Estimates By Age", DIRECTLY, ABOVE),
        HDim(impact_parameters, "Impact Parameters", DIRECTLY, LEFT),
    ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    # savepreviewhtml(tidy_sheet, fname=tab.name + "Preview.html")
    tidied_sheets.append(tidy_sheet.topandas())

tabs = [tab for tab in tabs if tab.name not in ['Cover_sheet', 'Notes']]
for tab in tabs:

    print(tab.name)

    anchor_1c = tab.excel_ref("A1")

    percentage_estimates_by_age_1c = anchor_1c.shift(1, 23).expand(RIGHT).is_not_blank().is_not_whitespace()
    
    impact_parameters_1c = tab.filter("Weighted count").expand(DOWN).is_not_blank().is_not_whitespace()
    
    observations_1c = impact_parameters_1c.waffle(percentage_estimates_by_age_1c)
    
    dimensions_1c = [
        HDim(percentage_estimates_by_age_1c, "Percentage Estimates By Age", DIRECTLY, ABOVE),
        HDim(impact_parameters_1c, "Impact Parameters", DIRECTLY, LEFT)
    ]
    tidy_sheet_1c = ConversionSegment(tab, dimensions_1c, observations_1c)
    # savepreviewhtml(tidy_sheet_1c, fname=tab.name + "Preview.html")
    tidied_sheets.append(tidy_sheet_1c.topandas())

df = pd.concat(tidied_sheets, sort = True).fillna('')

df

df["Impact Parameters"].unique()

df["Percentage Estimates By Age"].unique()

df["Percentage Estimates By Age"] = df["Percentage Estimates By Age"].replace(r'\n', '', regex = True)
# .map(lambda x: x.rstrip('\n% '))
# .replace(r'\n', '', regex = True)

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

df = df[['Percentage Estimates By Age','Impact Parameters', 'Confidence Intervals','OBS']]

df

df.rename(columns = {'OBS' : 'Value'}, inplace = True)

df.to_csv("observations.csv", index = False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')

# +
# Tabl1a:
# persons/population
# percentage

# Table1b:
# persons/population

