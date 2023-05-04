import shutil
import time
from datetime import datetime as dt

import pandas as pd
from loguru import logger as log
from watchdog.events import FileSystemEventHandler

# for explicit CIFS watching
from watchdog.observers.polling import PollingObserver as Observer

from common import (
    append_data_to_target_table,
    collect_deltas,
    get_watermark,
    load_data_into_dataframe,
)
from config import Settings
from database import WorkoutData


class MonitorFolder(FileSystemEventHandler):
    def __init__(self) -> None:
        log.info("Starting ETL Strong App")
        db = WorkoutData()
        db.set_table_name(Settings().target_table.split(".")[2])
        db.set_table_schema(Settings().target_table.split(".")[1])
        db.validate_table_exists()

    def on_created(self, event):
        def get_filename() -> str:
            return event.src_path.split("/")[-1]

        log.info(f"New file detected: '{get_filename()}' at path: '{event.src_path}'")

        def get_staged_file_full_path() -> str:
            return Settings().staging_path + "/" + get_filename()

        def move_file_to_staging_location() -> None:
            log.info(f"Copying '{get_filename()}' to '{get_staged_file_full_path()}'")
            try:
                shutil.move(event.src_path, get_staged_file_full_path())
            except Exception as e:
                log.error(e)

        def process_data() -> pd.DataFrame:
            try:
                processed_data = collect_deltas(
                    load_data_into_dataframe(get_staged_file_full_path()),
                    get_watermark(),
                )
                return processed_data
            except Exception as e:
                log.error(e)

        def get_processed_file_full_path() -> str:
            return (
                Settings().processed_path
                + "/"
                + str(dt.today().strftime("%Y-%m-%d %H%M"))
                + "_"
                + get_filename()
            )

        def move_file_to_processed() -> None:
            log.info(f"Moving '{get_filename()}' to '{get_processed_file_full_path()}'")
            try:
                shutil.move(get_staged_file_full_path(), get_processed_file_full_path())
            except Exception as e:
                log.error(e)

        ###########################################################################

        if get_filename() == Settings().expected_file:
            move_file_to_staging_location()
            append_data_to_target_table(
                df=process_data(),
                schema=Settings().target_table.split(".")[1],
                table=Settings().target_table.split(".")[2],
            )
            move_file_to_processed()
        else:
            log.warning(
                f"File '{get_filename()}' does not match the expected filename. Skipping..."
            )

    # def on_modified(self, event):
    #     # print(event.event_type, event.src_path, sep='\t')
    #     pass
    # def on_deleted(self, event):
    #     # print(event.event_type, event.src_path, sep='\t\t')
    #     pass
    def start(self) -> None:
        event_handler = MonitorFolder()
        watch_path = Settings().watch_path
        observer = Observer()
        observer.schedule(event_handler, watch_path, recursive=True)
        observer.start()
        log.info("Watchdog Monitor Running...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            log.info("Keyboard Interrupt Detected. Stopping Watchdog Monitor...")
        finally:
            observer.stop()
            observer.join()
