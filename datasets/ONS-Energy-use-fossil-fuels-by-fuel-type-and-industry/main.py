import json
import pandas as pandas
from gssutils import *

metadata = Scraper(seed="info.json")

metadata.dataset.comment = """ 
The UK's fuel use by industry (SIC 2007 group - around 130 categories) and type (coal, natural gas, petrol, diesel oil for road vehicles (DERV), 
fuel oil, gas oil, aviation fuel and other), 1990 to 2021. This dataset excludes biofuels and waste.

"""

metadata.dataset.description = """ 
The UK's fuel use by industry (SIC 2007 group - around 130 categories) and type (coal, natural gas, petrol, diesel oil for road vehicles (DERV), 
fuel oil, gas oil, aviation fuel and other), 1990 to 2021. This dataset excludes biofuels and waste.

"""

distribution = metadata.distribution(latest=True)

# reterieve the id from info.json for URI's (use later)
with open("info.json", "r") as read_file:
    data = json.load(read_file)
    title_id = data["id"]

def pathify_section_values(section):
    if "Total" in section:
        section = pathify(section)
        return section
    if "Travel" in section or "travel" in section:
        section = pathify(section)
        return section
    else:
        return section

tabs = distribution.as_databaker()

tidied_sheets = []
for tab in tabs:
    if tab.name in ["Contents", "Summary "]:
        continue
    elif tab.name == "Carbon based fuels ":
        # Processing only the top table
        remove_bottom_section1 = tab.excel_ref("A29").expand(DOWN).expand(RIGHT)
        year = tab.excel_ref("D5").expand(RIGHT).is_not_blank()
        section = tab.excel_ref("A6").expand(DOWN) - remove_bottom_section1
        section_name = tab.excel_ref("C6").expand(DOWN) - remove_bottom_section1
        observations = section_name.fill(RIGHT).is_not_blank()
        fuel = "Carbon based fuels"

        dimensions = [
            HDim(section, "Section Notation", DIRECTLY, LEFT),
            HDim(section_name, "Industry Section Name", DIRECTLY, LEFT),
            HDim(year, "Year", DIRECTLY, ABOVE),
            HDimConst("Fuel", fuel),
        ]
        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        # savepreviewhtml(tidy_sheet, fname = tab.name+ "Preview.html")
        table = tidy_sheet.topandas()

        # Creating a unified column for Section Notation and Industry Section Name
        table["Section"] = table.apply(
            lambda x: x["Industry Section Name"]
            if x["Section Notation"] == "-"
            else x["Industry Section Name"]
            if x["Section Notation"] == ""
            else x["Section Notation"],
            axis=1,
        )
        table["Section"] = table["Section"].apply(pathify_section_values)
        tidied_sheets.append(table)

    elif tab.name not in ["Aviation fuel", "Other"]:
        # Processing the top table
        remove_bottom_section = tab.excel_ref("A29").expand(DOWN).expand(RIGHT)
        year = tab.excel_ref("D5").expand(RIGHT).is_not_blank()
        section = tab.excel_ref("A6").expand(DOWN) - remove_bottom_section
        section_name = tab.excel_ref("C6").expand(DOWN) - remove_bottom_section
        observations = section_name.fill(RIGHT).is_not_blank()
        fuel = tab.name

        dimensions = [
            HDim(section, "Section Notation", DIRECTLY, LEFT),
            HDim(section_name, "Industry Section Name", DIRECTLY, LEFT),
            HDim(year, "Year", DIRECTLY, ABOVE),
            HDimConst("Fuel", fuel),
        ]
        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        # savepreviewhtml(tidy_sheet, fname = tab.name+ "Preview.html")
        table = tidy_sheet.topandas()

        # Creating a unified column for Section Notation and Industry Section Name
        table["Section"] = table.apply(
            lambda x: x["Industry Section Name"]
            if x["Section Notation"] == "-"
            else x["Industry Section Name"]
            if x["Section Notation"] == ""
            else x["Section Notation"],
            axis=1,
        )
        table["Section"] = table["Section"].apply(pathify_section_values)
        tidied_sheets.append(table)

        # Processing the bottom table
        remove_notes = tab.excel_ref("A162").expand(DOWN).expand(RIGHT)

        sic_group = tab.excel_ref("A31").expand(DOWN) - remove_notes
        section = tab.excel_ref("B31").expand(DOWN) - remove_notes
        section_name = tab.excel_ref("C31").expand(DOWN) - remove_notes
        observations = section_name.fill(RIGHT).is_not_blank()
        fuel = tab.name

        dimensions = [
            HDim(sic_group, "SIC(07)Group", DIRECTLY, LEFT),
            HDim(section, "Section Notation", DIRECTLY, LEFT),
            HDim(section_name, "Industry Section Name", DIRECTLY, LEFT),
            HDim(year, "Year", DIRECTLY, ABOVE),
            HDimConst("Fuel", fuel),
        ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        # savepreviewhtml(tidy_sheet, fname = tab.name+ "Preview.html")
        table = tidy_sheet.topandas()

        # Creating a unified column for SIC(07)Group, Section Notation and Industry Section Name
        table["Section"] = table.apply(
            lambda x: x["Industy Section Name"]
            if x["SIC(07)Group"] == "-"
            else x["SIC(07)Group"],
            axis=1,
        )

        table["Section"] = table["Section"].str.rstrip("0")
        table["Section"] = table["Section"].str.rstrip(".")
        table["Section"] = table["Section"].apply(lambda x: "{0:0>2}".format(x))
        table["Section"] = table["Section"].apply(pathify_section_values)
        table["Section"] = table["Section"].apply(pathify)
        tidied_sheets.append(table)

    elif tab.name == "Aviation fuel":
        # Processing the top table
        remove_bottom_section = tab.excel_ref("A12").expand(DOWN).expand(RIGHT)
        year = tab.excel_ref("E5").expand(RIGHT).is_not_blank()
        section = tab.excel_ref("A6").expand(DOWN) - remove_bottom_section
        section_name = tab.excel_ref("C6").expand(DOWN) - remove_bottom_section
        fuel = tab.excel_ref("D6").expand(DOWN) - remove_bottom_section
        observations = fuel.fill(RIGHT).is_not_blank()

        dimensions = [
            HDim(section, "Section Notation", DIRECTLY, LEFT),
            HDim(section_name, "Industry Section Name", DIRECTLY, LEFT),
            HDim(fuel, "Fuel", DIRECTLY, LEFT),
            HDim(year, "Year", DIRECTLY, ABOVE),
        ]
        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        # savepreviewhtml(tidy_sheet, fname = tab.name+ "Preview.html")
        table = tidy_sheet.topandas()

        # Creating a unified column for Section Notation and Industry Section Name
        table["Section"] = table.apply(
            lambda x: x["Industry Section Name"]
            if x["Section Notation"] == "-"
            else x["Industry Section Name"]
            if x["Section Notation"] == ""
            else x["Section Notation"],
            axis=1,
        )
        table["Section"] = table["Section"].apply(pathify_section_values)
        tidied_sheets.append(table)

        # Processing the bottom table
        remove_notes = tab.excel_ref("A25").expand(DOWN).expand(RIGHT)

        sic_group = tab.excel_ref("A18").expand(DOWN) - remove_notes
        section = tab.excel_ref("B18").expand(DOWN) - remove_notes
        section_name = tab.excel_ref("C18").expand(DOWN) - remove_notes
        fuel = tab.excel_ref("D18").expand(DOWN) - remove_notes
        observations = fuel.fill(RIGHT).is_not_blank()

        dimensions = [
            HDim(sic_group, "SIC(07)Group", DIRECTLY, LEFT),
            HDim(section, "Section Notation", DIRECTLY, LEFT),
            HDim(section_name, "Industry Section Name", DIRECTLY, LEFT),
            HDim(fuel, "Fuel", DIRECTLY, LEFT),
            HDim(year, "Year", DIRECTLY, ABOVE),
        ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        # savepreviewhtml(tidy_sheet, fname = tab.name+ "Preview.html")
        table = tidy_sheet.topandas()

        # Creating a unified column for SIC(07)Group, Section Notation and Industry Section Name
        table["Section"] = table.apply(
            lambda x: x["Industy Section Name"]
            if x["SIC(07)Group"] == "-"
            else x["SIC(07)Group"],
            axis=1,
        )

        table["Section"] = table["Section"].str.rstrip("0")
        table["Section"] = table["Section"].str.rstrip(".")
        table["Section"] = table["Section"].apply(lambda x: "{0:0>2}".format(x))
        table["Section"] = table["Section"].apply(pathify_section_values)
        table["Section"] = table["Section"].apply(pathify)
        tidied_sheets.append(table)

    elif tab.name == "Other":
        # Processing the middle table

        remove_bottom_section = tab.excel_ref("A51").expand(DOWN).expand(RIGHT)
        year = tab.excel_ref("D5").expand(RIGHT).is_not_blank()
        section = tab.excel_ref("A28").expand(DOWN) - remove_bottom_section
        section_name = tab.excel_ref("C28").expand(DOWN) - remove_bottom_section
        fuel = "Other fuels"
        observations = section_name.fill(RIGHT).is_not_blank()

        dimensions = [
            HDim(section, "Section Notation", DIRECTLY, LEFT),
            HDim(section_name, "Industry Section Name", DIRECTLY, LEFT),
            HDim(year, "Year", DIRECTLY, ABOVE),
            HDimConst("Fuel", fuel),
        ]
        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        # savepreviewhtml(tidy_sheet, fname = tab.name+ "Preview.html")
        table = tidy_sheet.topandas()

        # Creating a unified column for Section Notation and Industry Section Name
        table["Section"] = table.apply(
            lambda x: x["Industry Section Name"]
            if x["Section Notation"] == "-"
            else x["Industry Section Name"]
            if x["Section Notation"] == ""
            else x["Section Notation"],
            axis=1,
        )
        table["Section"] = table["Section"].apply(pathify_section_values)
        tidied_sheets.append(table)

        # Processing the bottom table
        remove_notes = tab.excel_ref("A184").expand(DOWN).expand(RIGHT)

        sic_group = tab.excel_ref("A53").expand(DOWN) - remove_notes
        section = tab.excel_ref("B53").expand(DOWN) - remove_notes
        section_name = tab.excel_ref("C53").expand(DOWN) - remove_notes
        fuel = "Other fuels"
        observations = section_name.fill(RIGHT).is_not_blank()

        dimensions = [
            HDim(sic_group, "SIC(07)Group", DIRECTLY, LEFT),
            HDim(section, "Section Notation", DIRECTLY, LEFT),
            HDim(section_name, "Industry Section Name", DIRECTLY, LEFT),
            HDim(year, "Year", DIRECTLY, ABOVE),
            HDimConst("Fuel", fuel),
        ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        # savepreviewhtml(tidy_sheet, fname = tab.name+ "Preview.html")
        table = tidy_sheet.topandas()

        # Creating a unified column for SIC(07)Group, Section Notation and Industry Section Name
        table["Section"] = table.apply(
            lambda x: x["Industy Section Name"]
            if x["SIC(07)Group"] == "-"
            else x["SIC(07)Group"],
            axis=1,
        )

        table["Section"] = table["Section"].str.rstrip("0")
        table["Section"] = table["Section"].str.rstrip(".")
        table["Section"] = table["Section"].apply(lambda x: "{0:0>2}".format(x))
        table["Section"] = table["Section"].apply(pathify_section_values)
        table["Section"] = table["Section"].apply(pathify)
        tidied_sheets.append(table)

    print(tab.name)

df = pd.concat(tidied_sheets, sort=True)

df.rename(columns={"OBS": "Value", "DATAMARKER": "Marker"}, inplace=True)
df["Year"] = df["Year"].astype(str).replace("\.0", "", regex=True)

df.replace(
    {
        "Marker": {"c": "confidential"},
        "Fuel": {
            "('DERV',)": "Derv",
            "Derv": "Diesel oil for road vehicles (DERV)",
            "Gas oil": "Gas oil including marine oil excluding DERV",
        },
        "Section": {
            "total": "grand-total",
            "Consumer expenditure": "consumer-expenditure",
        },
    },
    inplace=True,
)

# df["Fuel"] = df["Fuel"].str.rstrip(" ")
df["Year"] = df["Year"].astype(float).astype(int)

# indexNames = df[df["Section"] == ""].index
# df.drop(indexNames, inplace=True)

# info needed to create URI's for section
unique = (
    "http://gss-data.org.uk/data/gss_data/climate-change/"
    + title_id
    + "-concept/sic-2007/"
)
sic = "http://business.data.gov.uk/companies/def/sic-2007/"
# create the URI's from the section column

df["Section"] = df["Section"].map(
    lambda x: unique + x
    if "-" in x
    else (unique + x if "grand-total" in x else sic + x)
)

try:
    df["Fuel"] = df["Fuel"].apply(pathify)
except Exception as err:
    raise Exception('Failed to pathify column "{}".'.format(df["Fuel"])) from err

df = df[["Year", "Section", "Fuel", "Value", "Marker"]]

df.to_csv("observations.csv", index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file("catalog-metadata.json")