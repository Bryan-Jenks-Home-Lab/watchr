from sqlalchemy import DECIMAL, Column, DateTime, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base

from config import Settings

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

    def __repr__(self):
        return (
            "<WorkoutData("
            "row_id='{self.row_id}',"
            "date='{self.date}',"
            "workout_name='{self.workout_name}',"
            "duration='{self.duration}',"
            "exercise_name='{self.exercise_name}',"
            "set_order='{self.set_order}',"
            "weight='{self.weight}',"
            "reps='{self.reps}',"
            "distance='{self.distance}',"
            "seconds='{self.seconds}',"
            "notes='{self.notes}',"
            "workout_notes='{self.workout_notes}',"
            "rpe='{self.rpe}',"
            ")>".format(self=self)
        )

    def validate_table_exists(self):
        engine = create_engine(Settings().db_connection_string)
        Base.metadata.create_all(
            engine
        )  # Create the tables if they do not already exist
