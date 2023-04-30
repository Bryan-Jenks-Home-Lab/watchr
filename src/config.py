from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """https://docs.pydantic.dev/usage/settings/"""

    # app_name: str = Field(..., env="APP_NAME")
    # db_user: str = Field(..., env="DB_USER")
    # db_password: str = Field(..., env="DB_PASSWORD")
    # db_server: str = Field(..., env="DB_SERVER")
    # db_port: str = Field(..., env="DB_PORT")
    # db_database: str = Field(..., env="DB_DATABASE")
    db_connection_string: str = Field(..., env="DB_CONNECTION_STRING")

    watch_path: str = Field(..., env="WATCH_PATH")
    staging_path: str = Field(..., env="STAGING_PATH")
    processed_path: str = Field(..., env="PROCESSED_PATH")
    expected_file: str = Field(..., env="EXPECTED_FILE")

    target_table: str = Field(..., env="TARGET_TABLE")
