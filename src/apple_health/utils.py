import datetime as dt
import json
import os
import xml.etree.ElementTree as ET

import pandas as pd
from loguru import logger as log


def get_xml_file_root_element(file_path: str) -> ET.Element:
    tree = ET.parse(file_path)
    root = tree.getroot()
    return root


#: 0.1 Work on the file watcher module to pass events to the appropriate function
#: 0.2 flesh out the sqlalchemy table models


#: 1. Parse the xml data into a dataframe
#: 2. Get the watermark from the database and remove any data that is older than the watermark
#: 2.5 if the dataframe being processed is the clinical records dataframe, then join the json string to a new column
#: 3. Append the data to the database
#: 4. delete the file from the staging directory
#: 5. move the zip file to the processed directory


def parse_xml_data_to_df(
    root: ET.Element, desired_output: str
) -> pd.DataFrame | dt.datetime:
    if desired_output == "export_date":
        return dt.datetime.strptime(
            root.find(".//ExportDate").attrib.get("value"), "%Y-%m-%d %H:%M:%S %z"
        )
    if desired_output == "record":
        search_string = ".//Record"
        columns = [
            "type",
            "sourceName",
            "sourceVersion",
            "unit",
            "creationDate",
            "startDate",
            "endDate",
            "value",
            "device",
        ]
    if desired_output == "clinical_record":
        search_string = ".//ClinicalRecord"
        columns = [
            "type",
            "identifier",
            "sourceName",
            "sourceURL",
            "fhirVersion",
            "receivedDate",
            "resourceFilePath",
        ]

    data = []
    for record in root.findall(search_string):
        data.append(list(record.attrib.values()))
    df = pd.DataFrame(data, columns=columns)

    df["imported_on"] = dt.datetime.now()
    df["export_on"] = parse_xml_data_to_df(root, "export_date")
    final_column_order = ["imported_on", "export_on"] + columns

    if desired_output == "clinical_record":
        for index, row in df.iterrows():
            with open(row["resourceFilePath"]) as file:
                json_data = json.load(file)
                df.loc[index, "json"] = json_data
        # df["json"] =
        final_column_order = final_column_order + ["json"]

    df = df[final_column_order]

    return df


def remove_exist_json_file_data(json_dir):
    """This should grab the list of file names from the postgres database table
    from there it should delete any json data files matching that extracted list from the unzipped directory.
    """
    for filename in os.listdir(json_dir):
        if filename.endswith(".json"):
            file_path = os.path.join(json_dir, filename)
            os.remove(file_path)


# json_dir = "/Volumes/sql/services/watchr/outbound/apple_health_export/clinical-records"

# loaded_data = []
# columns = ["filename", "json_data"]

# for filename in os.listdir(json_dir):
#     if filename.endswith(".json"):
#         file_path = os.path.join(json_dir, filename)
#         with open(file_path) as file:
#             json_data = json.load(file)
#             loaded_data.append([filename, json_data])
# df = pd.DataFrame(loaded_data, columns=columns)
# print(df)
# df.to_csv("output.csv", index=False)

if __name__ == "__main__":
    file_path = "/Volumes/sql/services/watchr/outbound/apple_health_export/export.xml"
    root = get_xml_file_root_element(file_path)
    # df1 = parse_xml_data_to_df(root, "record")
    # print(df1.head())
    df2 = parse_xml_data_to_df(root, "clinical_record")
    print(df2["receivedDate"].min())
    print(df2["receivedDate"].max())
    ex_date = parse_xml_data_to_df(root, "export_date")
    print(ex_date)
    ...
