from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """https://docs.pydantic.dev/usage/settings/"""

    db_connection_string: str = Field(..., env="DB_CONNECTION_STRING")
    log_level: str = Field(..., env="LOG_LEVEL")

    pushover_user_key: str = Field(..., env="PUSHOVER_USER_KEY")
    pushover_api_token: str = Field(..., env="PUSHOVER_API_TOKEN")

    watch_path: str = Field(..., env="WATCH_PATH")
    staging_path: str = Field(..., env="STAGING_PATH")
    processed_path: str = Field(..., env="PROCESSED_PATH")

    strong_app_file: str = Field(..., env="STRONG_APP_FILE")
    strong_app_target_table: str = Field(..., env="STRONG_APP_TARGET_TABLE")

    apple_health_file: str = Field(..., env="APPLE_HEALTH_FILE")
    apple_health_target_table_records: str = Field(
        ..., env="APPLE_HEALTH_TARGET_TABLE_RECORDS"
    )
    apple_health_target_table_clinical_records: str = Field(
        ..., env="APPLE_HEALTH_TARGET_TABLE_CLINICAL_RECORDS"
    )
