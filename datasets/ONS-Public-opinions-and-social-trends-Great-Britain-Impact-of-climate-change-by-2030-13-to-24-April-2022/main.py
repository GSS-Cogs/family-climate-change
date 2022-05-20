# %%
import pandas as pd
from gssutils import *

metadata = Scraper(seed="info.json")
distribution = metadata.distribution(latest=True)
tabs = {tab.name: tab for tab in metadata.distribution(
    latest=True).as_databaker()}

# %%
tidied_sheets = []
for name, tab in tabs.items():
    if 'Cover_sheet' in name or 'Notes' in name:
        continue
    # table 1a and 1b
    question = tab.excel_ref('A15').expand(
        DOWN).is_not_blank() - tab.excel_ref('A22').expand(DOWN)
    age_gender = tab.excel_ref('B13').expand(RIGHT).is_not_blank()
    observations = question.fill(RIGHT).is_not_blank()
    dimensions = [
        HDim(question, "Question", DIRECTLY, LEFT),
        HDim(age_gender, "age_gender_to_split", DIRECTLY, ABOVE),
        HDimConst("Measure Type", ''),
        HDimConst("Unit", 'Percent'),
        
    ]
    c1 = ConversionSegment(tab, dimensions, observations)
    df = c1.topandas()
    tidied_sheets.append(df)

    # table 1c
    question = tab.excel_ref('A26').expand(DOWN).is_not_blank()
    age_gender = tab.excel_ref('B24').expand(RIGHT).is_not_blank()
    observations = question.fill(RIGHT).is_not_blank()
    dimensions = [
        HDim(question, "Question", DIRECTLY, LEFT),
        HDim(age_gender, "age_gender_to_split", DIRECTLY, ABOVE),
        HDim(question, "Measure Type", DIRECTLY, LEFT),
        HDimConst("Unit", 'Number'),

    ]
    c1 = ConversionSegment(tab, dimensions, observations)
    df = c1.topandas()
    tidied_sheets.append(df)

df = pd.concat(tidied_sheets, sort=True).fillna(
    '').replace(r'\r+|\n+|\t+', ' ', regex=True)

df.rename(columns={'OBS': 'Value'}, inplace=True)

df["Gender"] = df['age_gender_to_split'].apply(lambda x: 'Male' if 'Men' in x
                                               else ('Female' if 'Women' in x else 'all'))
df["Age"] = df['age_gender_to_split'].apply(lambda x: 'all' if 'Men' in x
                                            else ('all' if 'Women' in x else ('all' if 'All' in x else x)))
df["Measure Type"] = df.apply(lambda x: 'Percentage Estimates' if '%' in x['age_gender_to_split']
                              else 'Lower Confidence Interval' if 'LCL' in x['age_gender_to_split']
                              else 'Upper Confidence Interval' if 'UCL' in x['age_gender_to_split']
                              else x["Measure Type"], axis=1)

del df['age_gender_to_split']

df['Question'].replace({
    "Weighted count": "Not Applicable",
    "Sample size": "Not Applicable",
}, inplace=True)

df['Age'] = df['Age'].map(lambda x: x.lstrip('Aged ').rstrip(' %').rstrip(' UCL').rstrip(' LCL'))
df = df[["Question", "Gender", "Age", "Measure Type", "Unit", "Value"]]

# %%
df.to_csv("observations.csv", index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')
