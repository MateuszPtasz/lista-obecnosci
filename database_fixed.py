# database_fixed.py
# Ulepszona implementacja obsługi bazy danych z lepszym zarządzaniem połączeniami

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import logging

# Konfiguracja logowania
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='database.log',
    filemode='a'
)
logger = logging.getLogger("database")

SQLALCHEMY_DATABASE_URL = "sqlite:///./database.db"

# Konfiguracja silnika z parametrami wydajnościowymi
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={
        "check_same_thread": False,
        "timeout": 30
    },
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,  # odnawia połączenia po godzinie
    pool_pre_ping=True  # weryfikuje połączenie przed użyciem
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Generator do użycia w Depends
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Błąd bazy danych: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

# Context manager do ręcznego zarządzania sesją
@contextmanager
def db_session():
    """Context manager do bezpiecznego zarządzania sesją bazy danych"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        logger.error(f"Błąd bazy danych: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()
