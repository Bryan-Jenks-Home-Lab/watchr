from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """https://docs.pydantic.dev/usage/settings/"""

    db_connection_string: str = Field(..., env="DB_CONNECTION_STRING")

    watch_path: str = Field(..., env="WATCH_PATH")
    staging_path: str = Field(..., env="STAGING_PATH")
    processed_path: str = Field(..., env="PROCESSED_PATH")
    expected_file: str = Field(..., env="EXPECTED_FILE")

    target_table: str = Field(..., env="TARGET_TABLE")
