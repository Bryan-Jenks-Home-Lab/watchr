import pandas as pd
from config import Settings
from sqlalchemy import DECIMAL, Column, DateTime, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base

from models import FileProcessor

Base = declarative_base()


class WorkoutData(Base):
    __tablename__ = "Workout_data"
    __table_args__ = {"schema": "strongapp"}
    row_id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime)
    workout_name = Column(String)
    duration = Column(String)
    exercise_name = Column(String)
    set_order = Column(Integer)
    weight = Column(DECIMAL)
    reps = Column(Integer)
    distance = Column(Integer)
    seconds = Column(Integer)
    notes = Column(String)
    workout_notes = Column(String)
    rpe = Column(DECIMAL)

    @classmethod
    def set_table_name(self, table_name):
        self.__tablename__ = table_name

    @classmethod
    def set_table_schema(self, schema_name):
        self.__table_args__ = {"schema": schema_name}

    def validate_table_exists(self, connection_string):
        engine = create_engine(connection_string)
        Base.metadata.create_all(
            engine
        )  # Create the tables if they do not already exist


class StrongAppProcessor(FileProcessor):
    def __init__(self, new_file) -> None:
        super().__init__(new_file)
        self.target_table = Settings().strong_app_target_table
        self.watermark = self.get_watermark(
            target_table=self.target_table, connection_string=self.conn
        )
        _, self.schema, self.table = self.target_table.split(".")

    def validate_target_table_exists(self):
        strong_app = WorkoutData()
        strong_app.set_table_schema(self.schema)
        strong_app.set_table_name(self.table)
        strong_app.validate_table_exists(self.conn)

    def move_file_to_staging(self):
        self.move_file(self.new_file, self.staged_file)

    def load_data_into_df(self):
        self.loaded_data = self.load_csv_into_df(self.staged_file)

    def process_the_data(self) -> pd.DataFrame:
        self.delta_data = self.collect_deltas(self.loaded_data, self.watermark)

    def upload_new_data_to_target_table(self) -> None:
        self.append_data_to_target_table(self.delta_data, self.target_table, self.conn)

    def move_file_to_processed(self):
        self.move_file(self.staged_file, self.processed_file)

    def notification_content(self):
        notification_data = dict(
            title="Strong App Data Import",
            message=f"Successfully imported {self.delta_data.shape[0]} rows of data",
        )
        return notification_data
