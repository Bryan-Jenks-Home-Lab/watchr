import datetime as dt
import shutil

import pandas as pd
from config import Settings
from loguru import logger as log
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


class FileProcessor:
    def __init__(self, new_file: str) -> None:
        self.new_file = new_file
        self.file_name = self.get_filename(self.new_file)
        self.staged_file = self.get_staged_file_full_path(self.file_name)
        self.processed_file = self.get_processed_file_full_path(self.file_name)
        self.conn = Settings().db_connection_string

    def load_csv_into_df(self, file_path: str) -> pd.DataFrame:
        df = pd.read_csv(file_path, sep=",", header=0)
        df.columns = df.columns.str.replace(" ", "_").str.lower()

        log.success(f"Data loaded from {file_path} into a Pandas DataFrame")
        return df

    def collect_deltas(
        self, df: pd.DataFrame, watermark: dt.datetime, date_field: str = "date"
    ) -> pd.DataFrame:
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
            pd.Timestamp("1900-01-01 00:00:00", tz="UTC") if result is None else result
        )
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
        path = Settings().processed_path
        timestamp = str(dt.datetime.today().strftime("%Y-%m-%d %H%M"))
        return path + "/" + timestamp + "_" + file_name

    def get_filename(self, file_path: str) -> str:
        return file_path.split("/")[-1]
