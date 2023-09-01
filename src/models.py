import datetime as dt
import re
import shutil
import xml.etree.ElementTree as ET

import pandas as pd
from config import Settings
from loguru import logger as log
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


class FileProcessor:
    """The general file processor class that all other file processors inherit from including common methods and attributes."""

    def __init__(self, new_file: str) -> None:
        self.new_file = new_file
        self.file_name = self.get_filename(self.new_file)
        self.staged_file = self.get_staged_file_full_path(self.file_name)
        self.processed_file = self.get_processed_file_full_path(self.file_name)
        self.conn = Settings().db_connection_string

    def load_csv_into_df(self, file_path: str) -> pd.DataFrame:
        """Load a CSV file into a Pandas DataFrame, replacing column names with spaces in them with underscores and lowercasing all column names."""
        df = pd.read_csv(file_path, sep=",", header=0)
        df.columns = df.columns.str.replace(" ", "_").str.lower()

        log.success(f"Data loaded from {file_path} into a Pandas DataFrame")
        return df

    def collect_deltas(
        self, df: pd.DataFrame, watermark: pd.Timestamp, date_field: str
    ) -> pd.DataFrame:
        """Takes a Pandas DataFrame and returns a filtered DataFrame containing only records with a date greater than the watermark.
        The watermark is the maximum date in the target table.
        The provided date_field is the string name of the column containing the date field in the DataFrame.
        """
        log.info("Determining data deltas...")
        df[date_field] = pd.to_datetime(df[date_field])
        log.debug(f"{watermark = }")
        filtered_df = df[df[date_field] > watermark]
        log.debug(f"{filtered_df.shape = }")
        return filtered_df

    def generate_db_connection(self, connection_string) -> sessionmaker.object_session:
        engine = create_engine(connection_string)
        return engine

    def generate_db_session(self, connection_string) -> sessionmaker.object_session:
        engine = create_engine(connection_string)
        Session = sessionmaker(bind=engine)
        session = Session()
        return session

    def get_watermark(
        self, target_table: str, connection_string: str, watermark_field: str = "date"
    ) -> dt.datetime:
        query = text("SELECT MAX({}) FROM {};".format(watermark_field, target_table))
        session = self.generate_db_session(connection_string)
        result = session.execute(query).scalar()
        watermark = (
            pd.Timestamp(ts_input="1900-01-01 00:00:00") if result is None else result
        )
        log.debug(f"{watermark = }")
        return watermark

    def append_data_to_target_table(
        self, df: pd.DataFrame, target_table: str, connection_string: str
    ) -> None:
        _, schema, table = target_table.split(".")
        conn = self.generate_db_connection(connection_string)
        if df.shape[0] != 0:
            try:
                log.info(f"Beginning data import to {target_table}")
                df.to_sql(
                    name=table, con=conn, schema=schema, if_exists="append", index=False
                )
                log.success("Data import completed")
            except Exception as e:
                log.error(e)
        else:
            log.warning("No new data to import")

    def move_file(self, source: str, dest: str) -> None:
        log.info(f"Copying '{source.split('/')[-1]}' to '{dest}'")
        shutil.move(source, dest)

    def get_staged_file_full_path(self, file_path: str) -> str:
        return Settings().staging_path + "/" + file_path

    def get_processed_file_full_path(self, file_name: str) -> str:
        """Generate a full path to the processed file using the Settings class and the current timestamp prepended to the name of the now processed file."""
        path = Settings().processed_path
        timestamp = str(dt.datetime.today().strftime("%Y-%m-%d %H%M"))
        return path + "/" + timestamp + "_" + file_name

    def get_filename(self, file_path: str) -> str:
        """Get the filename from a full path by splitting the string on the '/' character and returning the last element in the resulting list."""
        return file_path.split("/")[-1]

    def get_xml_file_root_element(self, xml_file: str) -> ET.Element:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        return root

    def get_export_date(self, root: ET.Element) -> dt.datetime:
        """There is a single ExportDate element in the XML file that contains the date and time the export was created."""
        export_date = dt.datetime.strptime(
            root.find(".//ExportDate").attrib.get("value"), "%Y-%m-%d %H:%M:%S %z"
        )
        return export_date

    def generate_mapping(self, table: str):
        """Generate a mapping dictionary for the columns in the XML file to the columns in the target table.
        The columns are converted to snake_case and lowercased and the mapping is returned as a dictionary with the column names as the keys and the target table column names as the values.
        """
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

        for column in columns:
            name = column.replace(" ", "_")
            name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
            name = re.sub("([a-z0-9])([A-Z])", r"\1_\2", name)
            name = name.lower()
            mapping[column] = name

        return mapping
