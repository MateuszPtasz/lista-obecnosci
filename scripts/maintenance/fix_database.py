# fix_database_structure.py
import sqlite3
import os
from datetime import datetime

def fix_database():
    try:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        log_file = f"database_fix_{timestamp}.log"
        
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(f"=== Naprawa struktury bazy danych {timestamp} ===\n\n")
        
        def log(message):
            print(message)
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(message + "\n")
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Sprawdzenie tabeli shifts
        log("🔍 Sprawdzam tabelę shifts...")
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='shifts'")
        if not cursor.fetchone():
            log("   ❌ Tabela shifts nie istnieje!")
            conn.close()
            return
            
        # Pokaż strukturę tabeli shifts
        cursor.execute("PRAGMA table_info(shifts)")
        columns = cursor.fetchall()
        
        column_names = [col[1] for col in columns]
        log(f"   📋 Kolumny w tabeli shifts: {column_names}")
        
        # Sprawdź czy brakuje kolumn
        missing_columns = []
        if 'status' not in column_names:
            missing_columns.append('status')
        if 'is_holiday' not in column_names:
            missing_columns.append('is_holiday')
        if 'is_sick' not in column_names:
            missing_columns.append('is_sick')
        
        if missing_columns:
            log(f"   ⚠️ Brakujące kolumny: {missing_columns}")
            
            # Tworzenie kopii zapasowej
            backup_file = f"database_backup_{timestamp}.db"
            log(f"   📦 Tworzenie kopii zapasowej bazy danych: {backup_file}")
            import shutil
            shutil.copy2("database.db", backup_file)
            
            # Dodanie brakujących kolumn
            log("   🔧 Dodawanie brakujących kolumn...")
            
            for column in missing_columns:
                if column == 'status':
                    log("      - Dodaję kolumnę status...")
                    cursor.execute("ALTER TABLE shifts ADD COLUMN status TEXT DEFAULT 'Obecny'")
                elif column == 'is_holiday':
                    log("      - Dodaję kolumnę is_holiday...")
                    cursor.execute("ALTER TABLE shifts ADD COLUMN is_holiday BOOLEAN DEFAULT 0")
                elif column == 'is_sick':
                    log("      - Dodaję kolumnę is_sick...")
                    cursor.execute("ALTER TABLE shifts ADD COLUMN is_sick BOOLEAN DEFAULT 0")
            
            conn.commit()
            log("   ✅ Kolumny zostały dodane pomyślnie!")
            
            # Sprawdzenie po aktualizacji
            cursor.execute("PRAGMA table_info(shifts)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            log(f"   📋 Zaktualizowane kolumny w tabeli shifts: {column_names}")
        else:
            log("   ✅ Wszystkie wymagane kolumny już istnieją!")
        
        conn.close()
        log(f"\n✅ Zakończono naprawę bazy danych. Szczegóły w pliku: {log_file}")
        return log_file, True
        
    except Exception as e:
        error_msg = f"❌ Błąd: {e}"
        print(error_msg)
        if 'log' in locals() and 'log_file' in locals():
            log(error_msg)
            return log_file, False
        return None, False

if __name__ == "__main__":
    log_file, success = fix_database()
    print(f"Status naprawy: {'Sukces' if success else 'Błąd'}")
    if log_file:
        print(f"Szczegóły w pliku: {log_file}")
