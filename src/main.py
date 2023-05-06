from dotenv import load_dotenv

from file_watcher import MonitorFolder

load_dotenv()  # Load environment variables from .env file or docker environmental variables


def main():
    """At this point the environmental variables are loaded via `load_dotenv()`
    and the `MonitorFolder` class is instantiated and started.
    Environment variables are from either the `.env` file or docker environmental variables.
    """
    MonitorFolder().start()


if __name__ == "__main__":
    main()
