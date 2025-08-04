import sqlite3
import os
from datetime import datetime

def fix_database():
    try:
        # Utwórz kopię zapasową bazy danych
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
        
        # Wykonaj polecenia SQL bezpośrednio za pomocą sqlite3
        print("Wykonuję polecenia SQL...")
        
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        
        # Sprawdź czy kolumny już istnieją
        cursor.execute("PRAGMA table_info(shifts)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"Istniejące kolumny: {columns}")
        
        # Dodaj kolumny, jeśli nie istnieją
        if 'status' not in columns:
            print("Dodaję kolumnę 'status'")
            cursor.execute("ALTER TABLE shifts ADD COLUMN status TEXT DEFAULT 'Obecny'")
        else:
            print("Kolumna 'status' już istnieje")
            
        if 'is_holiday' not in columns:
            print("Dodaję kolumnę 'is_holiday'")
            cursor.execute("ALTER TABLE shifts ADD COLUMN is_holiday BOOLEAN DEFAULT 0")
        else:
            print("Kolumna 'is_holiday' już istnieje")
            
        if 'is_sick' not in columns:
            print("Dodaję kolumnę 'is_sick'")
            cursor.execute("ALTER TABLE shifts ADD COLUMN is_sick BOOLEAN DEFAULT 0")
        else:
            print("Kolumna 'is_sick' już istnieje")
        
        conn.commit()
        
        # Sprawdź strukturę tabeli po zmianach
        cursor.execute("PRAGMA table_info(shifts)")
        columns_after = [col[1] for col in cursor.fetchall()]
        print(f"Kolumny po zmianach: {columns_after}")
        
        conn.close()
        
        # Zapisz informacje o zmianach do pliku log
        with open("database_fix_log.txt", "w", encoding="utf-8") as log_file:
            log_file.write(f"Data naprawy: {datetime.now()}\n")
            log_file.write(f"Kopia zapasowa: {backup_file}\n")
            log_file.write(f"Kolumny przed zmianami: {columns}\n")
            log_file.write(f"Kolumny po zmianach: {columns_after}\n")
            
        print("Naprawa bazy danych zakończona.")
        return True
    
    except Exception as e:
        print(f"Wystąpił błąd podczas naprawy bazy danych: {e}")
        return False

if __name__ == "__main__":
    fix_database()
