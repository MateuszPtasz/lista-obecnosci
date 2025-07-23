# models.py

# Tutaj będą modele ORM

from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base
import datetime

class Shift(Base):
    __tablename__ = "shifts"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, index=True)
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    stop_time = Column(DateTime, nullable=True)
    start_location = Column(String, nullable=True)
    stop_location = Column(String, nullable=True)
    duration_min = Column(Integer, nullable=True)

class Rate(Base):
    __tablename__ = "rates"

    employee_id = Column(Integer, primary_key=True, index=True)
    regular_rate = Column(Float, default=25.0)
    saturday_rate = Column(Float, default=37.5)
    sunday_rate = Column(Float, default=50.0)

class AttendanceLog(Base):
    __tablename__ = "attendance_logs"

    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(String, index=True)
    start_time = Column(DateTime)
    start_lat = Column(Float)
    start_lon = Column(Float)
    stop_time = Column(DateTime, nullable=True)
    stop_lat = Column(Float, nullable=True)
    stop_lon = Column(Float, nullable=True)
    is_holiday = Column(String, default="nie")  # urlop: tak/nie
    is_sick = Column(String, default="nie")     # chorobowe: tak/nie/zus

class Employee(Base):
    __tablename__ = "employees"

    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    hourly_rate = Column(Float)
    rate_saturday = Column(Float, default=0.0)
    rate_sunday = Column(Float, default=0.0)
    rate_night = Column(Float, default=0.0)
    rate_overtime = Column(Float, default=0.0)
