from sqlalchemy import DECIMAL, Column, DateTime, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class AppleHealth(Base):
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

    def validate_table_exists(self, connection_string):
        engine = create_engine(connection_string)
        Base.metadata.create_all(
            engine
        )  # Create the tables if they do not already exist