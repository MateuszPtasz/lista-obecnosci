from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from database import SQLALCHEMY_DATABASE_URL
from work_models import WorkSession
from models import Employee

# Tworzenie silnika bazy danych
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Tworzenie bazy
Base = declarative_base()

# Tworzenie tabeli
WorkSession.__table__.create(bind=engine, checkfirst=True)

print("Tabela work_sessions została utworzona pomyślnie!")

# Aktualizacja modelu Employee, aby uwzględnić relację z WorkSession
# Nie jest to konieczne dla SQLite, ale może być potrzebne dla innych baz danych
try:
    import sqlalchemy as sa
    import sqlite3
    
    # Próba dodania kolumn first_name i last_name do tabeli employees
    # Używamy bezpośrednio SQLite dla prostoty
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Sprawdzamy czy kolumny istnieją
    cursor.execute("PRAGMA table_info(employees)")
    columns = {col[1] for col in cursor.fetchall()}
    
    if 'first_name' not in columns:
        cursor.execute('ALTER TABLE employees ADD COLUMN first_name TEXT')
        print("Dodano kolumnę first_name do tabeli employees")
        
    if 'last_name' not in columns:
        cursor.execute('ALTER TABLE employees ADD COLUMN last_name TEXT')
        print("Dodano kolumnę last_name do tabeli employees")
        
    if 'email' not in columns:
        cursor.execute('ALTER TABLE employees ADD COLUMN email TEXT')
        print("Dodano kolumnę email do tabeli employees")
        
    if 'user_id' not in columns:
        cursor.execute('ALTER TABLE employees ADD COLUMN user_id INTEGER')
        print("Dodano kolumnę user_id do tabeli employees")
    
    # Wypełnij kolumny first_name i last_name danymi z name
    cursor.execute("SELECT id, name FROM employees WHERE (first_name IS NULL OR last_name IS NULL) AND name IS NOT NULL")
    employees_to_update = cursor.fetchall()
    
    for emp_id, name in employees_to_update:
        name_parts = name.strip().split(" ", 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        
        cursor.execute("UPDATE employees SET first_name = ?, last_name = ? WHERE id = ?", 
                      (first_name, last_name, emp_id))
        print(f"Zaktualizowano dane dla pracownika {emp_id}: {first_name} {last_name}")
    
    conn.commit()
    conn.close()
except Exception as e:
    print(f"Nie można dodać kolumn: {str(e)}")
    print("Kontynuowanie bez zmian w tabeli employees.")

print("Operacje na bazie danych zakończone!")
