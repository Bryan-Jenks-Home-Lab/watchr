from loguru import logger as log

from apple_health.models import AppleHealthProcessor, AppleHealthRecordsProcessor


# common functions
def get_processor(file_name: str) -> dict[str, object]:
    """Import all the processors that the application should use.ß
    When a new file lands in the watched directory, take the file name with no extension and match that with the processor dictionary key to get the processor class.
    """
    processors = dict(
        export=AppleHealthProcessor,  # Process the export.zip file
        records=AppleHealthRecordsProcessor,  # Process the contents of the export.zip file
    )

    try:
        return processors.get(file_name.split(".")[0])
    except Exception as e:
        log.warning(
            f"File '{file_name}' does not match the expected filename. Skipping..."
        )
        log.error(e)


if __name__ == "__main__":
    pass
