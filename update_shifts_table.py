#!/usr/bin/env python3
"""
Skrypt do aktualizacji tabeli shifts, dodający brakujące kolumny dotyczące współrzędnych geograficznych
"""
import sqlite3
import os

# Ścieżka do bazy danych
DB_PATH = "database.db"

# Sprawdź czy plik bazy danych istnieje
if not os.path.exists(DB_PATH):
    print(f"❌ Plik bazy danych {DB_PATH} nie istnieje!")
    exit(1)

# Połącz z bazą danych
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    # Sprawdź czy kolumny już istnieją
    cursor.execute("PRAGMA table_info(shifts)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    # Wypisz istniejące kolumny
    print("Istniejące kolumny w tabeli shifts:")
    for name in column_names:
        print(f"  - {name}")
    
    # Kolumny do dodania jeśli nie istnieją
    columns_to_add = [
        {"name": "start_latitude", "type": "REAL"},
        {"name": "start_longitude", "type": "REAL"},
        {"name": "stop_latitude", "type": "REAL"},
        {"name": "stop_longitude", "type": "REAL"}
    ]
    
    # Dodaj brakujące kolumny
    for col in columns_to_add:
        if col["name"] not in column_names:
            print(f"Dodawanie kolumny: {col['name']} ({col['type']})")
            cursor.execute(f"ALTER TABLE shifts ADD COLUMN {col['name']} {col['type']}")
        else:
            print(f"Kolumna {col['name']} już istnieje")
    
    # Zatwierdź zmiany
    conn.commit()
    print("\n✅ Aktualizacja tabeli shifts zakończona pomyślnie!")
    
    # Sprawdź zaktualizowaną strukturę
    cursor.execute("PRAGMA table_info(shifts)")
    updated_columns = cursor.fetchall()
    print("\nZaktualizowane kolumny w tabeli shifts:")
    for col in updated_columns:
        print(f"  - {col[1]} ({col[2]})")
    
except Exception as e:
    print(f"❌ Błąd podczas aktualizacji tabeli: {str(e)}")
    conn.rollback()
    
finally:
    conn.close()
