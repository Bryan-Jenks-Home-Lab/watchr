from loguru import logger as log

from apple_health.models import (
    AppleHealthClinicalRecordsProcessor,
    AppleHealthProcessor,
    AppleHealthRecordsProcessor,
)
from strong_app.models import StrongAppProcessor


# common functions
def get_processor(file_name: str) -> dict[str, object]:
    processors = dict(
        strong=StrongAppProcessor,
        export=AppleHealthProcessor,
        records=AppleHealthRecordsProcessor,
        clinical_records=AppleHealthClinicalRecordsProcessor,
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
