import sys

import pretty_errors  # NOQA: F401
from config import Settings
from dotenv import load_dotenv
from file_watcher import MonitorFolder
from loguru import logger as log

# Load environment variables from .env file or docker environmental variables
load_dotenv()
# Remove the default logger configuration
log.remove()
# Add a new logger configuration with the desired log level
log.add(sink=sys.stdout, level=Settings().log_level)


def main():
    """At this point the environmental variables are loaded via `load_dotenv()`
    and the `MonitorFolder` class is instantiated and started.
    Environment variables are from either the `.env` file or docker environmental variables.
    """
    MonitorFolder().start()


if __name__ == "__main__":
    main()
