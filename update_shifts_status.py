"""
Skrypt do aktualizacji tabeli shifts - dodanie pól status, is_holiday i is_sick
"""

import sqlite3
import os
import sys
from datetime import datetime

def add_columns_to_shifts():
    """Dodaje nowe kolumny do tabeli shifts, jeśli jeszcze nie istnieją"""
    try:
        # Połączenie z bazą danych
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Sprawdzenie, czy kolumny już istnieją
        cursor.execute("PRAGMA table_info(shifts)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Dodaj kolumny, jeśli nie istnieją
        if 'status' not in columns:
            print("Dodaję kolumnę 'status' do tabeli shifts...")
            cursor.execute("ALTER TABLE shifts ADD COLUMN status TEXT DEFAULT 'Obecny'")
            
        if 'is_holiday' not in columns:
            print("Dodaję kolumnę 'is_holiday' do tabeli shifts...")
            cursor.execute("ALTER TABLE shifts ADD COLUMN is_holiday BOOLEAN DEFAULT 0")
            
        if 'is_sick' not in columns:
            print("Dodaję kolumnę 'is_sick' do tabeli shifts...")
            cursor.execute("ALTER TABLE shifts ADD COLUMN is_sick BOOLEAN DEFAULT 0")
        
        # Zatwierdź zmiany
        conn.commit()
        print("Baza danych została zaktualizowana pomyślnie!")
        
    except sqlite3.Error as e:
        print(f"Błąd SQLite: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Nieoczekiwany błąd: {e}")
        sys.exit(1)
    finally:
        if conn:
            conn.close()
            
def backup_database():
    """Tworzy kopię zapasową bazy danych przed migracją"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_file = f"database_backup_{timestamp}.db"
        
        # Sprawdź czy plik bazy danych istnieje
        if not os.path.exists("database.db"):
            print("Plik bazy danych (database.db) nie istnieje!")
            return False
            
        # Kopiuj bazę danych
        import shutil
        shutil.copy2("database.db", backup_file)
        print(f"Utworzono kopię zapasową bazy danych: {backup_file}")
        return True
    except Exception as e:
        print(f"Błąd podczas tworzenia kopii zapasowej: {e}")
        return False

if __name__ == "__main__":
    print("Rozpoczynam aktualizację bazy danych...")
    
    # Najpierw wykonaj kopię zapasową
    if backup_database():
        # Następnie dodaj kolumny
        add_columns_to_shifts()
    else:
        print("Anulowano aktualizację bazy danych.")
