import datetime as dt
import os
import xml.etree.ElementTree as ET
import zipfile

import pandas as pd
import pytz
from config import Settings
from loguru import logger as log
from sqlalchemy import Column, DateTime, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base

from common_python.pushover import Pushover
from models import FileProcessor

Base = declarative_base()


class AppleHealthRecords(Base):
    """This class is used to create the SQLAlchemy ORM object for the Apple Health Records table."""

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
        """Create the tables if they do not already exist"""
        engine = create_engine(connection_string)
        Base.metadata.create_all(engine)


class AppleHealthProcessor(FileProcessor):
    """This class is used to process the Apple Health export.zip file."""

    def __init__(self, zip_file) -> None:
        # Zip file path passed to class contructor
        log.debug(f"{zip_file = }")
        staged_file = self.decompress_zip_file(zip_file)
        root = self.get_xml_file_root_element(staged_file)
        export_date = self.get_export_date(root)
        records_df_columns = [
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

        records_df = self.make_dataframe_from_xml_query(
            root, ".//Record", records_df_columns
        )
        records_df.rename(columns=self.generate_mapping("records"), inplace=True)
        records_df["imported_on"] = dt.datetime.now()
        records_df["exported_on"] = export_date

        records_df.to_csv(Settings().watch_path + "/records.csv", index=False)

        log.success("Processed Apple Health Data Zipfile into CSV")

    def decompress_zip_file(self, zip_file: str):
        """Decompress a zip file to a specified directory and return the path to the decompressed directory"""
        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            zip_ref.extractall(Settings().staging_path)
            extracted_files = zip_ref.namelist()
        # Grab the name of the decompressed folder and append it to the staging path
        # in order to decompress it in the staging area
        log.debug(f"{extracted_files[0] = }")
        staged_directory = os.path.join(Settings().staging_path, extracted_files[0])
        log.debug(f"{staged_directory = }")
        # Delete the zip file from the inbound directory
        os.remove(zip_file)
        return staged_directory

    def make_dataframe_from_xml_query(
        self, root: ET.Element, query: str, columns: list
    ) -> pd.DataFrame:
        records_data = []
        for record in root.findall(query):
            records_data.append(list(record.attrib.values()))
        df = pd.DataFrame(records_data, columns=columns)
        return df


class AppleHealthRecordsProcessor(FileProcessor):
    """This class is used to process the Apple Health records.csv file."""

    def __init__(self, new_file: str) -> None:
        log.info("AppleHealthRecordsProcessor")
        # Move the file to the staging area
        staged_file = self.get_staged_file_full_path(new_file.split("/")[-1])
        self.move_file(new_file, staged_file)
        # Check that the target database table exists
        self.validate_target_table_exists()
        # Load the data into a dataframe
        df = self.load_csv_into_df(staged_file)
        # Remove records with types that we do not want to import
        # prevents import errors due to bad data from apple devices
        records_to_keep = df["type"].isin(self.get_desired_record_types())
        df = df[records_to_keep]
        log.debug(f"{df.shape = }")
        # Acquire the watermark for the target table
        watermark = self.get_watermark(
            target_table=Settings().apple_health_target_table_records,
            connection_string=Settings().db_connection_string,
            watermark_field="creation_date",
        )
        timezone = pytz.FixedOffset(-420)
        watermark = watermark.replace(tzinfo=timezone)
        log.debug(f"{watermark = }")
        # Filter out the records that have already been imported
        self.delta_df = self.collect_deltas(df, watermark, date_field="creation_date")
        log.debug(f"{self.delta_df.shape = }")
        # Organize the columns in the dataframe for the target table
        self.delta_df = self.delta_df[self.get_table_columns()]
        log.debug(f"{self.delta_df.columns = }")
        # Rename the columns to match the target table
        self.delta_df.rename(columns=self.generate_mapping("records"), inplace=True)
        log.debug(f"{self.delta_df.columns}")
        # Overwrite input file with only the deltas so retention doesnt grow exponentially
        self.delta_df.to_csv(staged_file, index=False)
        # Begin the data load process
        log.info("Loading data to target table")
        self.append_data_to_target_table(
            self.delta_df,
            Settings().apple_health_target_table_records,
            Settings().db_connection_string,
        )
        # Move the file to the processed area
        processed_file = self.get_processed_file_full_path(staged_file.split("/")[-1])
        self.move_file(staged_file, processed_file)

        log.success("Processed Apple Health Records Data")
        self.send_notification()

    def validate_target_table_exists(self):
        _, self.schema, self.table = Settings().apple_health_target_table_records.split(
            "."
        )
        apple_table = AppleHealthRecords()
        apple_table.set_table_schema(self.schema)
        apple_table.set_table_name(self.table)
        apple_table.validate_table_exists(Settings().db_connection_string)

    def get_desired_record_types(self) -> list[str]:
        return [
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

    def get_table_columns(self) -> list[str]:
        """This is the order and format of the columns in the target table."""
        return [
            "imported_on",
            "exported_on",
            "type",
            "source_name",
            "source_version",
            "unit",
            "creation_date",
            "start_date",
            "end_date",
            "value",
            "device",
        ]

    def send_notification(self):
        """Send pushover notification"""
        notification_data = dict(
            token=Settings().pushover_api_token,
            user=Settings().pushover_user_key,
            title="Apple Health Records Data Import",
            message=f"Successfully imported {self.delta_df.shape[0]} rows of data",
        )
        pushover = Pushover(**notification_data)
        pushover.send_notification()
