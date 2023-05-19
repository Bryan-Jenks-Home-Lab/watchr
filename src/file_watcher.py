import time
from datetime import datetime as dt

from config import Settings
from loguru import logger as log
from watchdog.events import FileSystemEventHandler

# for explicit CIFS watching
from watchdog.observers.polling import PollingObserver as Observer

# from src.common import get_processors
from apple_health.service import process_apple_health_file
from strong_app.service import process_oura_ring_file, process_strong_app_file


class MonitorFolder(FileSystemEventHandler):
    def __init__(self) -> None:
        log.info("Starting Watchr")
        log.info("Validating Strong App Table Exists")

    def on_created(self, event):
        log.info(f"New file detected: '{event.src_path}'")
        new_file = event.src_path.split("/")[-1]

        # TODO change the process function into a class with methods and state
        # make a parent class for inheritable methods
        # in this function make it so the input file selects the correct class from a dictionary of key value pairs of key to class initializer
        # then the same standard variable holds the instantiated class like `data_file = processors.get(new_file)()`

        # data_file = get_processors(new_file)(event.src_path)

        try:
            if new_file == Settings().strong_app_file:
                process_strong_app_file(event.src_path)
            elif new_file == Settings().apple_health_file:
                process_apple_health_file(event.src_path)
                # TODO - add apple health file processing
            elif new_file == Settings().oura_file:
                ...  # TODO - add oura ring file processing
            else:
                log.warning(
                    f"File '{new_file}' does not match the expected filename. Skipping..."
                )
        except Exception as e:
            log.error(e)

    # def on_modified(self, event):
    #     # print(event.event_type, event.src_path, sep='\t')
    #     pass

    # def on_deleted(self, event):
    #     log.info(event.src_path.split("/")[-1] + " was deleted")

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
