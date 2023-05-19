from config import Settings
from loguru import logger as log

from common import (
    append_data_to_target_table,
    collect_deltas,
    get_filename,
    get_processed_file_full_path,
    get_staged_file_full_path,
    get_watermark,
    load_csv_into_df,
    move_file,
)
from strong_app.models import WorkoutData


def process_strong_app_file(new_file: str) -> None:
    try:
        target_table = Settings().strong_app_target_table
        filename = get_filename(new_file)
        staged_file = get_staged_file_full_path(filename)
        conn = Settings().db_connection_string
        watermark = get_watermark(target_table=target_table, connection_string=conn)
        _, schema, table = target_table.split(".")
        # solidify metadata and verify the table exists
        strong_app = WorkoutData()
        strong_app.set_table_schema(schema)
        strong_app.set_table_name(table)
        strong_app.validate_table_exists(conn)
        # move file to staging directory
        move_file(new_file, staged_file)
        # load data deltas into a dataframe
        data = load_csv_into_df(staged_file)
        processed_data = collect_deltas(data, watermark)
        # append data to target database table
        append_data_to_target_table(
            df=processed_data, target_table=target_table, connection_string=conn
        )
        # Move file to processed directory
        processed_location = get_processed_file_full_path(filename)
        move_file(source=staged_file, dest=processed_location)
    except Exception as e:
        log.error(e)
