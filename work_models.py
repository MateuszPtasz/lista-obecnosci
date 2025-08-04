from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import datetime as dt

class WorkSession(Base):
    """Model do przechowywania informacji o sesji pracy pracownika."""
    __tablename__ = "work_sessions"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, ForeignKey("employees.id"), index=True)
    
    # Czas rozpoczęcia i zakończenia
    start_time = Column(DateTime, default=dt.datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    
    # Lokalizacje
    start_lat = Column(Float, nullable=True)
    start_lon = Column(Float, nullable=True)
    end_lat = Column(Float, nullable=True)
    end_lon = Column(Float, nullable=True)
    
    # Dodatkowe informacje
    duration_minutes = Column(Integer, nullable=True)
    emergency_end = Column(Boolean, default=False)  # Czy sesja została awaryjnie zakończona
    notes = Column(String, nullable=True)
    
    # Relacja z pracownikiem
    employee = relationship("Employee", back_populates="work_sessions")

# Relacja zostanie dodana w main.py po zaimportowaniu obu modeli
