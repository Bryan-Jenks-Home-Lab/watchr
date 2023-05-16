import datetime as dt

import pandas as pd
from config import Settings
from loguru import logger as log
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


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


def generate_db_connection(connection_string) -> sessionmaker.object_session:
    engine = create_engine(connection_string)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def get_watermark(target_table, connection_string) -> dt.datetime:
    query = text("SELECT MAX(date) FROM {};".format(target_table))
    session = generate_db_connection(connection_string)
    result = session.execute(query).scalar()
    watermark = pd.Timestamp("1900-01-01") if result is None else result
    return watermark


def append_data_to_target_table(df: pd.DataFrame, table: str, schema: str) -> None:
    log.debug(type(df))
    log.debug(df)
    if df.shape[0] != 0:
        log.info("Beginning data import to database table")
        df.to_sql(
            name=table,
            con=generate_db_connection(),
            schema=schema,
            if_exists="append",
            index=False,
        )
        log.success("Data import completed")
    else:
        log.warning("No new data to import")
