import datetime as dt
import os
import re
import shutil
import zipfile

import pandas as pd
from config import Settings
from loguru import logger as log
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from apple_health.service import process_apple_health_file
from strong_app.service import process_oura_ring_file, process_strong_app_file


class FileProcessor:
    def collect_deltas(self, df: pd.DataFrame, watermark: dt.datetime) -> pd.DataFrame:
        log.info("Determining data deltas...")
        df["date"] = pd.to_datetime(df["date"])
        log.debug(f"{watermark = }")
        filtered_df = df[df["date"] > watermark]
        log.debug(f"{filtered_df.shape = }")
        return filtered_df


def get_processors(file_name: str) -> dict[str, object]:
    processors = dict(
        strong=process_strong_app_file,
        export=process_apple_health_file,
        oura=process_oura_ring_file,
    )
    return processors.get(file_name.split(".")[0])


def camel_to_snake(name):
    # TODO this is to be used on the apple health data, general application not needed to all incoming files
    # Use regular expressions to split camel case into separate words
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    name = re.sub("([a-z0-9])([A-Z])", r"\1_\2", name)
    # Convert to lowercase and join with underscores
    name = name.lower()
    # new_columns = [camel_to_snake(col) for col in df.columns]
    # df.columns = new_columns
    return name


def decompress_zip_file(zip_file_path: str, destination_path: str) -> str:
    with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
        zip_ref.extractall(destination_path)
        extracted_files = zip_ref.namelist()

    # Assuming that the first item in the list is the root directory
    decompressed_directory = os.path.join(destination_path, extracted_files[0])
    return decompressed_directory


def load_csv_into_df(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path, sep=",", header=0)
    df.columns = df.columns.str.replace(" ", "_").str.lower()

    log.success(f"Data loaded from {file_path} into a Pandas DataFrame")
    return df


def generate_db_connection(connection_string) -> sessionmaker.object_session:
    engine = create_engine(connection_string)
    return engine


def generate_db_session(connection_string) -> sessionmaker.object_session:
    engine = create_engine(connection_string)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def get_watermark(
    target_table: str, connection_string: str, watermark_field: str = "date"
) -> dt.datetime:
    query = text("SELECT MAX({}) FROM {};".format(watermark_field, target_table))
    session = generate_db_session(connection_string)
    result = session.execute(query).scalar()
    watermark = pd.Timestamp("1900-01-01") if result is None else result
    return watermark


def append_data_to_target_table(
    df: pd.DataFrame, target_table: str, connection_string: str
) -> None:
    _, schema, table = target_table.split(".")
    conn = generate_db_connection(connection_string)
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


def move_file(source: str, dest: str) -> None:
    log.info(f"Copying '{source.split('/')[-1]}' to '{dest}'")
    try:
        shutil.move(source, dest)
    except Exception as e:
        log.error(e)


def get_staged_file_full_path(file_path: str) -> str:
    return Settings().staging_path + "/" + file_path


def get_processed_file_full_path(file_path: str) -> str:
    return (
        Settings().processed_path
        + "/"
        + str(dt.datetime.today().strftime("%Y-%m-%d %H%M"))
        + "_"
        + file_path
    )


def get_filename(file_path: str) -> str:
    return file_path.split("/")[-1]


if __name__ == "__main__":
    pass
