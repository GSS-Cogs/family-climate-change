import json
import pandas as pandas
from gssutils import *

info = json.load(open("info.json"))
metadata = Scraper(seed="info.json")
metadata.dataset.comment = "The emissions of carbon dioxide, methane, nitrous oxide, hydro-fluorocarbons, perfluorocarbons, sulphur hexafluoride, nitrogen trifluoride and total greenhouse gas emissions, by industry (SIC 2007 group – around 130 categories), UK, 1990 to 2021"
metadata.dataset.description = "The emissions of carbon dioxide, methane, nitrous oxide, hydro-fluorocarbons, perfluorocarbons, sulphur hexafluoride, nitrogen trifluoride and total greenhouse gas emissions, by industry (SIC 2007 group – around 130 categories), UK, 1990 to 2021."
# -
distribution = metadata.distribution(latest=True)

# reterieve the id from info.json for URI's (use later)
title_id = info["id"]

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
    if "Contents" in tab.name:
        continue
    elif tab.name in ["GHG total", "Total GHG"]:
        remove_bottom_section = tab.excel_ref("A28").expand(DOWN).expand(RIGHT)
        year = tab.excel_ref("D4").expand(RIGHT).is_not_blank()
        section = tab.excel_ref("A5").expand(DOWN) - remove_bottom_section
        section_name = tab.excel_ref("C5").expand(DOWN) - remove_bottom_section
        observations = year.fill(DOWN).is_not_blank() - remove_bottom_section
        measure_type = "Mass of air emissions of carbon dioxide equivalent"

        dimensions = [
            HDim(section, "Section Notation", DIRECTLY, LEFT),  # will be dropped
            HDim(
                section_name, "Industry Section Name", DIRECTLY, LEFT
            ),  # will be dropped
            HDim(year, "Year", DIRECTLY, ABOVE),
            HDimConst("Emission Type", tab.name),
            HDimConst("Measure Type", measure_type),
        ]
        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        # savepreviewhtml(tidy_sheet, fname = tab.name+ "Preview.html")
        table = tidy_sheet.topandas()
        # table.replace({'                      - Not travel': 'Consumer expenditure - Not travel',
        #                '                      - Travel': 'Consumer expenditure - travel'
        #                }, inplace=True)
        table["Section"] = table.apply(
            lambda x: x["Industry Section Name"]
            if x["Section Notation"] == "-"
            else x["Industry Section Name"]
            if x["Section Notation"] == ""
            else x["Section Notation"],
            axis=1,
        )

        tidied_sheets.append(table)

    else:
        remove_bottom_section = tab.excel_ref("A28").expand(DOWN).expand(RIGHT)
        year = tab.excel_ref("D4").expand(RIGHT).is_not_blank()
        section = tab.excel_ref("A5").expand(DOWN) - remove_bottom_section
        section_name = tab.excel_ref("C5").expand(DOWN) - remove_bottom_section
        observations = year.fill(DOWN).is_not_blank() - remove_bottom_section
        if tab.name == "CO2":
            measure_type = "Mass of air emissions"
        else:
            measure_type = "Mass of air emissions of carbon dioxide equivalent"

        dimensions = [
            HDim(section, "Section Notation", DIRECTLY, LEFT),  # will be dropped
            HDim(
                section_name, "Industry Section Name", DIRECTLY, LEFT
            ),  # will be dropped
            HDim(year, "Year", DIRECTLY, ABOVE),
            HDimConst("Emission Type", tab.name),
            HDimConst("Measure Type", measure_type),
        ]
        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        # savepreviewhtml(tidy_sheet, fname = tab.name+ "Preview.html")
        table = tidy_sheet.topandas()
        # table.replace(
        #     {
        #         "                      - Not travel": "Consumer expenditure - Not travel",
        #         "                      - Travel": "Consumer expenditure - travel",
        #     },
        #     inplace=True,
        # )
        table["Section"] = table.apply(
            lambda x: x["Industry Section Name"]
            if x["Section Notation"] == "-"
            else x["Industry Section Name"]
            if x["Section Notation"] == ""
            else x["Section Notation"],
            axis=1,
        )

        tidied_sheets.append(table)

        # Bottom part
        # remove_top_section = tab.excel_ref('A27').expand(UP).expand(RIGHT)
        remove_notes = tab.excel_ref("A162").expand(DOWN).expand(RIGHT)

        sic_group = tab.excel_ref("A31").expand(DOWN) - remove_notes
        section = tab.excel_ref("B31").expand(DOWN) - remove_notes
        section_name = tab.excel_ref("C31").expand(DOWN) - remove_notes
        observations = section_name.fill(RIGHT).is_not_blank()

        dimensions = [
            HDim(sic_group, "SIC(07)Group", DIRECTLY, LEFT),
            HDim(section, "Section Notation", DIRECTLY, LEFT),  # will be dropped
            HDim(
                section_name, "Industry Section Name", DIRECTLY, LEFT
            ),  # will be dropped
            HDim(year, "Year", DIRECTLY, ABOVE),
            HDimConst("Emission Type", tab.name),
            HDimConst("Measure Type", measure_type),
        ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        # savepreviewhtml(tidy_sheet, fname = tab.name+ "Preview.html")
        table = tidy_sheet.topandas()
        table["Section"] = table.apply(
            lambda x: x["Industy Section Name"]
            if x["SIC(07)Group"] == "-"
            else x["SIC(07)Group"],
            axis=1,
        )

        table["Section"] = table["Section"].str.rstrip("0")
        table["Section"] = table["Section"].str.rstrip(".")
        table["Section"] = table["Section"].apply(lambda x: "{0:0>2}".format(x))
    
        tidied_sheets.append(table)

df = pd.concat(tidied_sheets, sort=True)

# +
df.rename(columns={"OBS": "Value", "DATAMARKER": "Marker"}, inplace=True)
df["Year"] = df["Year"].astype(str).replace("\.0", "", regex=True)

df = df.replace(
    {
        "Section": {
            "Consumer expenditure": "consumer-expenditure",
            "Total greenhouse gas emissions": "grand-total",
            "Total CO2 emissions": "grand-total",
            "Total CH4 emissions": "grand-total",
            "Total N2O emissions": "grand-total",
            "Total HFC emissions": "grand-total",
            "Total PFC emissions": "grand-total",
            "Total NF3 emissions": "grand-total",
            "Total SF6 emissions": "grand-total",
        }
    }
)

# df["Section"] = df["Section"].apply(pathify_section_values)
# df["Section"] = df["Section"].apply(pathify)

# info needed to create URI's for section
unique = (
    "http://gss-data.org.uk/data/gss_data/climate-change/"
    + title_id
    + "-concept/sic-2007/"
)
sic = "http://business.data.gov.uk/companies/def/sic-2007/"
# create the URI's from the section column

df["Section"] = df["Section"].map(
    lambda x: unique + x if "-" in x else (unique + x if "total" in x else sic + x)
)

df["Emission Type"] = df["Emission Type"].str.rstrip(" ")
df = df.replace(
    {
        "Emission Type": {
            "GHG total": "total-greenhouse-gases",
            "GHG Total": "total-greenhouse-gases",
            "Total GHG": "total-greenhouse-gases",
        }
    }
)

df["Unit"] = df.apply(
    lambda x: "kilotonnes-of-carbon-dioxide-equivalent"
    if "carbon dioxide" in x["Measure Type"]
    else "kilotonnes",
    axis=1,
)
# -
for col in ["Measure Type", "Unit"]:
    try:
        df[col] = df[col].apply(pathify)
    except Exception as err:
        raise Exception('Failed to pathify column "{}".'.format(col)) from err

# only need the following columns
df = df[["Year", "Section", "Emission Type", "Measure Type", "Unit", "Value"]]

df.to_csv("observations.csv", index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file("catalog-metadata.json")