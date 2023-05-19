from config import Settings
from loguru import logger as log

from common import decompress_zip_file


def process_apple_health_file(new_file: str) -> None:
    try:
        decompressed_data = decompress_zip_file(new_file, Settings().staging_path)
        print(decompressed_data)
    except Exception as e:
        log.error(e)
