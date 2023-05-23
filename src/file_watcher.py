import time

from config import Settings
from loguru import logger as log
from watchdog.events import FileSystemEventHandler

# for explicit CIFS watching
from watchdog.observers.polling import PollingObserver as Observer

from common import get_processor
from common_python.pushover import Pushover


class MonitorFolder(FileSystemEventHandler):
    def __init__(self) -> None:
        log.info("Starting Watchr")
        log.info("Validating Strong App Table Exists")

    def on_created(self, event):
        log.info(f"New file detected: '{event.src_path}'")
        new_file = event.src_path.split("/")[-1].split(".")[0]

        file_processor = get_processor(new_file)(event.src_path)

        file_processor.validate_target_table_exists()
        file_processor.move_file_to_staging()
        file_processor.load_data_into_df()
        file_processor.process_the_data()
        file_processor.upload_new_data_to_target_table()
        file_processor.move_file_to_processed()  # ⚠️
        notification_data = dict(
            token=Settings().pushover_api_token,
            user=Settings().pushover_user_key,
        )
        notification_data.update(file_processor.notification_content())
        pushover = Pushover(**notification_data)
        pushover.send_notification()

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
