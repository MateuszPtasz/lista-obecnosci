import sqlite3
import os
from datetime import datetime

def rebuild_shifts_table():
    """Przebudowuje tabelę shifts z nowymi kolumnami, zachowując istniejące dane"""
    try:
        # Utwórz kopię zapasową bazy danych
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_file = f"database_backup_{timestamp}.db"
        
        if os.path.exists("database.db"):
            import shutil
            shutil.copy2("database.db", backup_file)
            print(f"Utworzono kopię zapasową bazy danych: {backup_file}")
        else:
            print("Plik bazy danych nie istnieje!")
            return False
        
        # Połącz z bazą danych
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        
        # 1. Pobierz wszystkie dane z tabeli shifts
        cursor.execute("SELECT * FROM shifts")
        rows = cursor.fetchall()
        
        # 2. Pobierz informacje o kolumnach
        cursor.execute("PRAGMA table_info(shifts)")
        columns_info = cursor.fetchall()
        column_names = [col[1] for col in columns_info]
        print(f"Istniejące kolumny: {column_names}")
        
        # 3. Zmień nazwę obecnej tabeli
        cursor.execute("ALTER TABLE shifts RENAME TO shifts_old")
        
        # 4. Utwórz nową tabelę shifts ze wszystkimi potrzebnymi kolumnami
        cursor.execute('''
        CREATE TABLE shifts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT,
            start_time TIMESTAMP,
            stop_time TIMESTAMP,
            start_location TEXT,
            stop_location TEXT,
            start_latitude REAL,
            start_longitude REAL,
            stop_latitude REAL,
            stop_longitude REAL,
            duration_min INTEGER,
            status TEXT DEFAULT 'Obecny',
            is_holiday BOOLEAN DEFAULT 0,
            is_sick BOOLEAN DEFAULT 0
        )
        ''')
        
        # 5. Przygotuj dane do wstawienia
        data_to_insert = []
        column_str = ", ".join(column_names)
        
        placeholders = ", ".join(["?" for _ in column_names])
        
        # 6. Przenieś dane ze starej tabeli do nowej
        cursor.execute(f"INSERT INTO shifts ({column_str}) SELECT {column_str} FROM shifts_old")
        
        # 7. Usuń starą tabelę
        cursor.execute("DROP TABLE shifts_old")
        
        # 8. Zatwierdź zmiany
        conn.commit()
        
        # Sprawdź strukturę tabeli po zmianach
        cursor.execute("PRAGMA table_info(shifts)")
        new_columns = [col[1] for col in cursor.fetchall()]
        print(f"Kolumny po zmianach: {new_columns}")
        
        # Zapisz log operacji
        with open("database_rebuild_log.txt", "w", encoding="utf-8") as log_file:
            log_file.write(f"Data przebudowy: {datetime.now()}\n")
            log_file.write(f"Kopia zapasowa: {backup_file}\n")
            log_file.write(f"Stare kolumny: {column_names}\n")
            log_file.write(f"Nowe kolumny: {new_columns}\n")
            log_file.write(f"Liczba przeniesionych wierszy: {len(rows)}\n")
        
        conn.close()
        print("Przebudowa tabeli shifts zakończona pomyślnie!")
        return True
        
    except Exception as e:
        print(f"Wystąpił błąd podczas przebudowy tabeli: {e}")
        return False

if __name__ == "__main__":
    rebuild_shifts_table()
