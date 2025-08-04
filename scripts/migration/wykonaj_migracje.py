"""
Ten skrypt wykonuje migrację bazy danych - dodaje kolumny status, is_holiday i is_sick do tabeli shifts
"""

import sqlite3
import sys
from datetime import datetime
import os

def main():
    print("Rozpoczynam aktualizację bazy danych...")
    
    try:
        # Połączenie z bazą danych
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Sprawdzenie, czy kolumny już istnieją
        cursor.execute("PRAGMA table_info(shifts)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Dodaj kolumny, jeśli nie istnieją
        changes_made = False
        
        if 'status' not in columns:
            print("Dodaję kolumnę 'status' do tabeli shifts...")
            cursor.execute("ALTER TABLE shifts ADD COLUMN status TEXT DEFAULT 'Obecny'")
            changes_made = True
            
        if 'is_holiday' not in columns:
            print("Dodaję kolumnę 'is_holiday' do tabeli shifts...")
            cursor.execute("ALTER TABLE shifts ADD COLUMN is_holiday BOOLEAN DEFAULT 0")
            changes_made = True
            
        if 'is_sick' not in columns:
            print("Dodaję kolumnę 'is_sick' do tabeli shifts...")
            cursor.execute("ALTER TABLE shifts ADD COLUMN is_sick BOOLEAN DEFAULT 0")
            changes_made = True
        
        # Zatwierdź zmiany
        conn.commit()
        
        if changes_made:
            print("Baza danych została zaktualizowana pomyślnie!")
        else:
            print("Wszystkie kolumny już istnieją, nie wymagana aktualizacja.")
            
        # Wyświetl strukturę tabeli po zmianach
        cursor.execute("PRAGMA table_info(shifts)")
        columns = cursor.fetchall()
        print("\nAktualna struktura tabeli shifts:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]}, default: {col[4]})")
        
    except sqlite3.Error as e:
        print(f"Błąd SQLite: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Nieoczekiwany błąd: {e}")
        sys.exit(1)
    finally:
        if 'conn' in locals() and conn:
            conn.close()

    print("\nZakończono proces migracji.")

if __name__ == "__main__":
    main()
