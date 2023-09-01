import time

from config import Settings
from loguru import logger as log
from watchdog.events import FileSystemEventHandler

# for explicit CIFS watching
from watchdog.observers.polling import PollingObserver as Observer

from common import get_processor


class MonitorFolder(FileSystemEventHandler):
    def __init__(self) -> None:
        log.info("Starting Watchr")

    def on_created(self, event):
        log.info(f"New file detected: '{event.src_path}'")
        new_file_name_only = event.src_path.split("/")[-1].split(".")[0]

        # This is fetching the correct class to process the file based on the file name without
        # a file extension and then the `(event.src_path)` portion is initializing the class
        # with the new file path
        # All logic for file processing is contained within the __init__ method of the processor class
        get_processor(new_file_name_only)(event.src_path)

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
