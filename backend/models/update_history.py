from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UpdateHistory(Base):
    __tablename__ = "update_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    car_id = Column(Integer)
    field = Column(String)
    old_value = Column(String)
    new_value = Column(String)
    updated_by = Column(String)
    timestamp = Column(String)