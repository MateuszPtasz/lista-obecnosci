#!/usr/bin/env python3
import sqlite3

# Połącz z bazą danych
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

try:
    # Stwórz tabelę employees
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id TEXT PRIMARY KEY,
            name TEXT,
            hourly_rate REAL,
            rate_saturday REAL DEFAULT 0.0,
            rate_sunday REAL DEFAULT 0.0,
            rate_night REAL DEFAULT 0.0,
            rate_overtime REAL DEFAULT 0.0,
            pin TEXT
        )
    ''')
    
    # Stwórz tabelę attendance_logs jeśli nie istnieje
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            worker_id TEXT,
            start_time DATETIME,
            start_lat REAL,
            start_lon REAL,
            stop_time DATETIME,
            stop_lat REAL,
            stop_lon REAL,
            is_holiday TEXT DEFAULT 'nie',
            is_sick TEXT DEFAULT 'nie'
        )
    ''')
    
    # Stwórz tabelę shifts jeśli nie istnieje
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shifts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT,
            start_time DATETIME,
            stop_time DATETIME,
            start_location TEXT,
            stop_location TEXT,
            start_latitude REAL,
            start_longitude REAL,
            stop_latitude REAL,
            stop_longitude REAL,
            duration_min INTEGER
        )
    ''')

    # Stwórz tabelę pin_access_logs jeśli nie istnieje
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pin_access_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            worker_id TEXT,
            device_id TEXT,
            pin_entered TEXT,
            pin_correct INTEGER,
            access_granted INTEGER,
            location TEXT,
            device_model TEXT,
            os_version TEXT,
            app_version TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    print("✅ Wszystkie tabele zostały utworzone!")
    
    # Sprawdź strukturę
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("\nTabele w bazie danych:")
    for table in tables:
        print(f"  - {table[0]}")
        
except Exception as e:
    print(f"❌ Błąd: {e}")
    
finally:
    conn.close()
