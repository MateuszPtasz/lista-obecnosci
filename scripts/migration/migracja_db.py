"""
Ten skrypt wykonuje migrację bazy danych - dodaje kolumny status, is_holiday i is_sick do tabeli shifts
Skrypt działa w bieżącym katalogu, niezależnie od ścieżki wywołania.
"""

import sqlite3
import sys
import os
from datetime import datetime

# Pobierz ścieżkę bieżącego katalogu
current_dir = os.path.dirname(os.path.abspath(__file__))

# Utwórz ścieżki do plików
db_path = os.path.join(current_dir, "database.db")
log_path = os.path.join(current_dir, "migracja_log.txt")

def log_message(message):
    """Zapisz wiadomość do pliku log i wyświetl na ekranie"""
    print(message)
    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(message + "\n")

def main():
    # Utwórz plik log
    with open(log_path, "w", encoding="utf-8") as log_file:
        log_file.write(f"=== Log migracji bazy danych - {datetime.now()} ===\n\n")
    
    log_message(f"Rozpoczynam aktualizację bazy danych: {db_path}")
    
    try:
        # Połączenie z bazą danych
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Sprawdzenie, czy kolumny już istnieją
        cursor.execute("PRAGMA table_info(shifts)")
        columns = [col[1] for col in cursor.fetchall()]
        
        log_message(f"Znalezione kolumny w tabeli shifts: {columns}")
        
        # Dodaj kolumny, jeśli nie istnieją
        changes_made = False
        
        if 'status' not in columns:
            log_message("Dodaję kolumnę 'status' do tabeli shifts...")
            cursor.execute("ALTER TABLE shifts ADD COLUMN status TEXT DEFAULT 'Obecny'")
            changes_made = True
            
        if 'is_holiday' not in columns:
            log_message("Dodaję kolumnę 'is_holiday' do tabeli shifts...")
            cursor.execute("ALTER TABLE shifts ADD COLUMN is_holiday BOOLEAN DEFAULT 0")
            changes_made = True
            
        if 'is_sick' not in columns:
            log_message("Dodaję kolumnę 'is_sick' do tabeli shifts...")
            cursor.execute("ALTER TABLE shifts ADD COLUMN is_sick BOOLEAN DEFAULT 0")
            changes_made = True
        
        # Zatwierdź zmiany
        conn.commit()
        
        if changes_made:
            log_message("Baza danych została zaktualizowana pomyślnie!")
        else:
            log_message("Wszystkie kolumny już istnieją, nie wymagana aktualizacja.")
            
        # Wyświetl strukturę tabeli po zmianach
        cursor.execute("PRAGMA table_info(shifts)")
        columns = cursor.fetchall()
        
        log_message("\nAktualna struktura tabeli shifts:")
        for col in columns:
            log_message(f"  - {col[1]} ({col[2]}, default: {col[4]})")
        
    except sqlite3.Error as e:
        log_message(f"Błąd SQLite: {e}")
        sys.exit(1)
    except Exception as e:
        log_message(f"Nieoczekiwany błąd: {e}")
        sys.exit(1)
    finally:
        if 'conn' in locals() and conn:
            conn.close()

    log_message("\nZakończono proces migracji.")

if __name__ == "__main__":
    main()
