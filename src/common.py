import datetime as dt

import pandas as pd
from loguru import logger as log
from sqlalchemy import create_engine

from config import Settings


def load_data_into_dataframe(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path, sep=",", header=0)
    df.columns = df.columns.str.replace(" ", "_").str.lower()
    log.success(f"Data loaded from {file_path} into a Pandas DataFrame")
    return df


def collect_deltas(df: pd.DataFrame, watermark: dt.datetime) -> pd.DataFrame:
    log.info("Determining data deltas...")
    df["date"] = pd.to_datetime(df["date"])
    log.debug(f"{watermark = }")
    filtered_df = df[df["date"] > watermark]
    log.debug(f"{filtered_df.shape = }")
    return filtered_df


def get_watermark() -> dt.datetime:
    conn = generate_db_connection()
    query = "SELECT MAX(date) FROM {};".format(Settings().target_table)
    df = pd.read_sql_query(query, conn)
    watermark = df.iloc[0, 0]
    watermark = pd.Timestamp("1900-01-01") if watermark is None else watermark
    return watermark


def generate_db_connection() -> None:
    return create_engine(Settings().db_connection_string)


def append_data_to_target_table(df: pd.DataFrame, table: str, schema: str) -> None:
    print(type(df))
    print(df)
    if df.shape[0] != 0:
        log.info(f"Beginning data import to database table")
        df.to_sql(
            name=table,
            con=generate_db_connection(),
            schema=schema,
            if_exists="append",
            index=False,
        )
        log.success(f"Data import completed")
    else:
        log.warning(f"No new data to import")
