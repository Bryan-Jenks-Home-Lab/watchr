from dotenv import load_dotenv

from file_watcher import MonitorFolder

load_dotenv()  # Load environment variables from .env file or docker environmental variables


def main():
    MonitorFolder().start()


if __name__ == "__main__":
    main()
