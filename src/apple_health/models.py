import datetime as dt
import json
import os
import re
import xml.etree.ElementTree as ET
import zipfile

import pandas as pd
from config import Settings
from loguru import logger as log
from sqlalchemy import Column, DateTime, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base

from models import FileProcessor

Base = declarative_base()

# P1 - Apple Health Data split workflow so that it is taking the zip file and actually creating the 2 CSV's to be loaded into the database and then processing those 2 files separately under their own operations


class AppleHealthRecords(Base):
    __table_args__ = {"schema": "apple"}
    __tablename__ = "records"
    row_id = Column(Integer, primary_key=True, autoincrement=True)
    imported_on = Column(DateTime)
    exported_on = Column(DateTime)
    type = Column(String)
    source_name = Column(String)
    source_version = Column(String)
    unit = Column(String)
    creation_date = Column(DateTime)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    value = Column(String)
    device = Column(String)

    @classmethod
    def set_table_name(self, table_name):
        self.__tablename__ = table_name

    @classmethod
    def set_table_schema(self, schema_name):
        self.__table_args__ = {"schema": schema_name}

    def validate_table_exists(self, connection_string):
        engine = create_engine(connection_string)
        Base.metadata.create_all(
            engine
        )  # Create the tables if they do not already exist


class AppleHealthClinicalRecords(Base):
    __table_args__ = {"schema": "apple"}
    __tablename__ = "clinical_records"
    row_id = Column(Integer, primary_key=True, autoincrement=True)
    imported_on = Column(DateTime)
    exported_on = Column(DateTime)
    type = Column(String)
    identifier = Column(String)
    source_name = Column(String)
    source_url = Column(String)
    fhir_version = Column(String)
    received_date = Column(DateTime)
    resource_file_path = Column(String)
    json = Column(String)

    @classmethod
    def set_table_name(self, table_name):
        self.__tablename__ = table_name

    @classmethod
    def set_table_schema(self, schema_name):
        self.__table_args__ = {"schema": schema_name}

    def validate_table_exists(self, connection_string):
        engine = create_engine(connection_string)
        Base.metadata.create_all(
            engine
        )  # Create the tables if they do not already exist


class AppleHealthProcessor(FileProcessor):
    def __init__(self, new_file) -> None:
        # Zip file path passed to class contructor
        # We do not neet to init the parent class as this is a special case of multiple tables from separate files in a zip
        self.zip_file = new_file
        # Database connection string for later uploads (this is cookie cutter and not table specific)
        self.conn = Settings().db_connection_string
        # There are two tables that we are going to be processing so we need 2 target table variables
        self.records_target_table = Settings().apple_health_target_table_records
        self.clinical_records_target_table = (
            Settings().apple_health_target_table_clinical_records
        )

        #################

        # self.file_name = self.get_filename(self.new_file)
        # self.staged_file = self.get_staged_file_full_path(self.file_name)
        # self.processed_file = self.get_processed_file_full_path(self.file_name)

    def validate_target_table_exists(self):
        _, self.schema, self.table = self.records_target_table.split(".")
        apple_table = AppleHealthRecords()
        apple_table.set_table_schema(self.schema)
        apple_table.set_table_name(self.table)
        apple_table.validate_table_exists(self.conn)

        _, self.schema, self.table = self.clinical_records_target_table.split(".")
        apple_table = AppleHealthClinicalRecords()
        apple_table.set_table_schema(self.schema)
        apple_table.set_table_name(self.table)
        apple_table.validate_table_exists(self.conn)

    def move_file_to_staging(self):
        """Decompress a zip file to a specified directory and return the path to the decompressed directory"""
        with zipfile.ZipFile(self.zip_file, "r") as zip_ref:
            zip_ref.extractall(Settings().staging_path)
            extracted_files = zip_ref.namelist()
        self.staged_file = os.path.join(Settings().staging_path, extracted_files[0])
        # self.move_file_to_staging(self.zip_file, self.staged_file)
        self.staged_zip_file = (
            Settings().staging_path + "/" + self.zip_file.split("/")[-1]
        )
        log.debug(f"{self.staged_zip_file = }")
        self.move_file(self.zip_file, self.staged_zip_file)

    def load_data_into_df(self):
        # Class instance variables now set for the root xml element and the export date of the data
        self._get_xml_file_root_element()
        self._get_export_date()

        self.table = self.records_target_table.split(".")[-1]
        log.debug(f"{self.table = }")
        self._get_target_search_string(
            "records"
        )  # Get the search string to parse for in the xml data base on the table name
        log.debug(f"{self.target_search_string = }")
        self.data = []
        for record in self.root.findall(self.target_search_string):
            self.data.append(list(record.attrib.values()))
        self.records_df = pd.DataFrame(
            self.data, columns=self._get_target_table_columns("records")
        )

        self.table = self.clinical_records_target_table.split(".")[-1]
        log.debug(f"{self.table = }")
        self._get_target_search_string(
            "clinical_records"
        )  # Get the search string to parse for in the xml data base on the table name
        log.debug(f"{self.target_search_string = }")
        self.data = []
        # Parse the xml data into a dataframe
        for record in self.root.findall(self.target_search_string):
            self.data.append(list(record.attrib.values()))
        self.clinical_records_df = pd.DataFrame(
            self.data, columns=self._get_target_table_columns("clinical_records")
        )

    def process_the_data(self) -> pd.DataFrame:
        # Get watermarks for each table
        self.record_watermark = self.get_watermark(
            target_table=self.records_target_table,
            connection_string=self.conn,
            watermark_field="end_date",
        )
        self.clinical_record_watermark = self.get_watermark(
            target_table=self.clinical_records_target_table,
            connection_string=self.conn,
            watermark_field="received_date",
        )

        record_types = [
            "HKQuantityTypeIdentifierBodyFatPercentage",
            "HKQuantityTypeIdentifierBodyMass",
            "HKQuantityTypeIdentifierBodyMassIndex",
            "HKQuantityTypeIdentifierDietaryBiotin",
            "HKQuantityTypeIdentifierDietaryCaffeine",
            "HKQuantityTypeIdentifierDietaryChromium",
            "HKQuantityTypeIdentifierDietaryFolate",
            "HKQuantityTypeIdentifierDietaryMagnesium",
            "HKQuantityTypeIdentifierDietaryMolybdenum",
            "HKQuantityTypeIdentifierDietaryNiacin",
            "HKQuantityTypeIdentifierDietaryPantothenicAcid",
            "HKQuantityTypeIdentifierDietaryVitaminA",
            "HKQuantityTypeIdentifierDietaryVitaminB12",
            "HKQuantityTypeIdentifierDietaryVitaminB6",
            "HKQuantityTypeIdentifierDietaryVitaminC",
            "HKQuantityTypeIdentifierDietaryVitaminD",
            "HKQuantityTypeIdentifierDietaryVitaminE",
            "HKQuantityTypeIdentifierDietaryWater",
            "HKQuantityTypeIdentifierDietaryZinc",
            "HKQuantityTypeIdentifierLeanBodyMass",
            "HKQuantityTypeIdentifierWaistCircumference",
        ]

        # records_to_remove = all(self.records_df["type"] not in record_types)
        # self.records_df = self.records_df[~records_to_remove]
        # del records_to_remove
        records_to_keep = self.records_df["type"].isin(record_types)
        self.records_df = self.records_df[records_to_keep]
        log.debug(f"{self.records_df.shape = }")
        # records_to_remove = (
        #     pd.to_datetime(self.records_df["creationDate"]) < self.record_watermark
        # )
        # self.records_delta_data = self.records_df[~records_to_remove]

        # Filter the dataframes based on the watermarks to just deltas
        self.records_delta_data = self.collect_deltas(
            self.records_df, self.record_watermark, date_field="creationDate"
        )

        log.debug(f"{self.records_delta_data.shape = }")

        self.clinical_records_delta_data = self.collect_deltas(
            self.clinical_records_df,
            self.clinical_record_watermark,
            date_field="receivedDate",
        )

        log.debug(f"{self.clinical_records_delta_data.shape = }")

        # Add additional metadata columns to the dataframes
        self.records_delta_data["imported_on"] = dt.datetime.now()
        self.records_delta_data["exported_on"] = self.export_date

        self.clinical_records_delta_data["imported_on"] = dt.datetime.now()
        self.clinical_records_delta_data["exported_on"] = self.export_date

        self.records_final_column_order = (
            ["imported_on"]
            + ["exported_on"]
            + self._get_target_table_columns("records")
        )
        self.clinical_records_final_column_order = [
            "imported_on",
            "exported_on",
        ] + self._get_target_table_columns("clinical_records")

        # Add the json data to the clinical records dataframe
        # records table has to go first as the clinical records table will mutate the final column list variable
        self.records_delta_data = self.records_delta_data[
            self.records_final_column_order
        ]
        log.debug(f"{self.records_delta_data.columns = }")
        log.debug(f"{self.records_delta_data.shape = }")

        # TODO LEFT OFF HERE <++>

        log.info("Adding json data to clinical records dataframe")

        for index, row in self.clinical_records_delta_data.iterrows():
            json_file_path = (
                Settings().staging_path
                + "/apple_health_export"
                + row["resourceFilePath"]
            )

            log.debug(f"{json_file_path = }")
            with open(json_file_path) as file:
                json_data = str(json.load(file))
                self.clinical_records_delta_data.loc[index, "json"] = [json_data]

        self.clinical_records_delta_data = self.clinical_records_delta_data[
            self.clinical_records_final_column_order + ["json"]
        ]

        log.debug("Made it to column renaming")
        # Format the column names as they will be reflected in the database

        log.debug(f"{self.records_delta_data.columns}")
        self.records_delta_data.rename(
            columns=self._generate_mapping("records"), inplace=True
        )
        log.debug(f"{self.records_delta_data.columns}")

        log.debug(f"{self.clinical_records_delta_data.columns}")
        self.clinical_records_delta_data.rename(
            columns=self._generate_mapping("clinical_records"), inplace=True
        )
        log.debug(f"{self.clinical_records_delta_data.columns}")

    def upload_new_data_to_target_table(self) -> None:
        self.append_data_to_target_table(
            self.records_delta_data, self.records_target_table, self.conn
        )
        self.append_data_to_target_table(
            self.clinical_records_delta_data,
            self.clinical_records_target_table,
            self.conn,
        )

    def move_file_to_processed(self):
        # TODO LEFT OFF HERE <++>
        # TODO at this point i dont want to retain any of these files because of the size, and its full truncate and load, so just delete the files, the zip might also have been left in inbound, just in case check and remove it too
        self.move_file(self.staged_file, self.processed_file)
        log.critical("made it this far")
        exit()

    def notification_content(self):
        notification_data = dict(
            title="Apple Health Data Import",
            message=f"Successfully imported {self.delta_data.shape[0]} rows of data",
        )
        return notification_data

    def _get_xml_file_root_element(self) -> ET.Element:
        tree = ET.parse(self.staged_file)
        self.root = tree.getroot()

    def _get_export_date(self) -> dt.datetime:
        self.export_date = dt.datetime.strptime(
            self.root.find(".//ExportDate").attrib.get("value"), "%Y-%m-%d %H:%M:%S %z"
        )

    def _get_target_table_columns(self, table: str) -> list:
        if table == "records":
            return [
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
        if table == "clinical_records":
            return [
                "type",
                "identifier",
                "sourceName",
                "sourceURL",
                "fhirVersion",
                "receivedDate",
                "resourceFilePath",
            ]

    def _get_target_search_string(self, table: str) -> str:
        if table == "records":
            self.target_search_string = ".//Record"
        if table == "clinical_records":
            self.target_search_string = ".//ClinicalRecord"

    # def _camel_to_snake(self, name):
    #     name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    #     name = re.sub("([a-z0-9])([A-Z])", r"\1_\2", name)
    #     name = name.lower()
    #     return name

    def _generate_mapping(self, table: str):
        mapping = {}
        if table == "records":
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
        elif table == "clinical_records":
            columns = [
                "type",
                "identifier",
                "sourceName",
                "sourceURL",
                "fhirVersion",
                "receivedDate",
                "resourceFilePath",
            ]

        for column in columns:
            name = column.replace(" ", "_")
            name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
            name = re.sub("([a-z0-9])([A-Z])", r"\1_\2", name)
            name = name.lower()
            mapping[column] = name

        return mapping
