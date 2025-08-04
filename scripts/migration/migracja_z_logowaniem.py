"""
Ten skrypt wykonuje migrację bazy danych i zapisuje wyniki do pliku log.
"""

import sqlite3
import sys
from datetime import datetime
import os

def main():
    log_file = "migracja_log.txt"
    with open(log_file, "w") as f:
        f.write("Rozpoczynam aktualizację bazy danych...\n")
    
    try:
        # Połączenie z bazą danych
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Sprawdzenie, czy kolumny już istnieją
        cursor.execute("PRAGMA table_info(shifts)")
        columns = [col[1] for col in cursor.fetchall()]
        
        with open(log_file, "a") as f:
            f.write(f"Znalezione kolumny w tabeli shifts: {columns}\n")
        
        # Dodaj kolumny, jeśli nie istnieją
        changes_made = False
        
        if 'status' not in columns:
            with open(log_file, "a") as f:
                f.write("Dodaję kolumnę 'status' do tabeli shifts...\n")
            cursor.execute("ALTER TABLE shifts ADD COLUMN status TEXT DEFAULT 'Obecny'")
            changes_made = True
            
        if 'is_holiday' not in columns:
            with open(log_file, "a") as f:
                f.write("Dodaję kolumnę 'is_holiday' do tabeli shifts...\n")
            cursor.execute("ALTER TABLE shifts ADD COLUMN is_holiday BOOLEAN DEFAULT 0")
            changes_made = True
            
        if 'is_sick' not in columns:
            with open(log_file, "a") as f:
                f.write("Dodaję kolumnę 'is_sick' do tabeli shifts...\n")
            cursor.execute("ALTER TABLE shifts ADD COLUMN is_sick BOOLEAN DEFAULT 0")
            changes_made = True
        
        # Zatwierdź zmiany
        conn.commit()
        
        if changes_made:
            with open(log_file, "a") as f:
                f.write("Baza danych została zaktualizowana pomyślnie!\n")
        else:
            with open(log_file, "a") as f:
                f.write("Wszystkie kolumny już istnieją, nie wymagana aktualizacja.\n")
            
        # Wyświetl strukturę tabeli po zmianach
        cursor.execute("PRAGMA table_info(shifts)")
        columns = cursor.fetchall()
        
        with open(log_file, "a") as f:
            f.write("\nAktualna struktura tabeli shifts:\n")
            for col in columns:
                f.write(f"  - {col[1]} ({col[2]}, default: {col[4]})\n")
        
    except sqlite3.Error as e:
        with open(log_file, "a") as f:
            f.write(f"Błąd SQLite: {e}\n")
        sys.exit(1)
    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"Nieoczekiwany błąd: {e}\n")
        sys.exit(1)
    finally:
        if 'conn' in locals() and conn:
            conn.close()

    with open(log_file, "a") as f:
        f.write("\nZakończono proces migracji.\n")

if __name__ == "__main__":
    main()
