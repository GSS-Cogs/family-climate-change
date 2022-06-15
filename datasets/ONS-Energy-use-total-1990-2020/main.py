# %%
from gssutils import *

metadata = Scraper(seed="info.json")
distribution = metadata.distribution(latest = True)
# %%
tabs = distribution.as_databaker()
tidied_sheets = []
for tab in tabs:
    if 'Contents' in tab.name:
        continue
    
    year = tab.excel_ref('B4').expand(RIGHT).is_not_blank() 
    unit = tab.excel_ref('AF3')
    remove_note = tab.filter(contains_string("Notes")).expand(DOWN).expand(RIGHT)
    source = tab.excel_ref('A4').expand(DOWN).is_bold().is_not_whitespace() - remove_note 
    industry_section = tab.excel_ref('A4').expand(DOWN).is_not_blank().is_not_whitespace() - remove_note
    observations = year.fill(DOWN).is_not_blank() - remove_note 
    
    dimensions = [
        HDim(year, 'Year', DIRECTLY, ABOVE),
        HDim(source, "Energy Consumption Source", CLOSEST, ABOVE),
        HDim(industry_section, "Industry Section", DIRECTLY, LEFT),
        HDim(unit, 'Unit', CLOSEST, ABOVE),
    ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    df = tidy_sheet.topandas()
    tidied_sheets.append(df)
# %%
df = pd.concat(tidied_sheets, sort=True)
df.rename(columns={'OBS' : 'Value'}, inplace=True)
df['Year'] = df['Year'].astype(str).replace('\.0', '', regex=True)
df["Industry Section"] = df["Industry Section"].str.lstrip('- ')
df['Industry Section'] = df['Industry Section'].str.replace("Arts, entertainment and recreation; other service activities", "Arts, entertainment and recreation")
df['Industry Section'] = df['Industry Section'].apply(pathify)
df["Unit"]= df['Unit'].str.extract('.*\((.*)\).*')
df['Unit'] = df['Unit'].str.replace("Mtoe","Million tonnes of oil equivalent").str.strip()
df = pd.pivot_table(df, values = 'Value', index=['Energy Consumption Source','Industry Section', 'Year'], columns = 'Unit').reset_index() 
df.rename(columns={'PJ' : 'Value'}, inplace=True)
df = df[['Year', 'Energy Consumption Source', 'Industry Section', 'Value', 'Million tonnes of oil equivalent']]
# %%
metadata.dataset.title = "Energy use: total 1990 - 2020"
df.to_csv('observations.csv', index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')