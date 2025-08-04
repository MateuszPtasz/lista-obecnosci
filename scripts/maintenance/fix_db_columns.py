import sqlite3
import os
import sys
from datetime import datetime

def fix_database_full():
    """Naprawia bazę danych i wyświetla szczegółowe informacje"""
    try:
        # Utwórz plik log z unikalną nazwą
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"database_fix_{timestamp}.log"
        log_file = open(log_filename, "w", encoding="utf-8")
        
        def log(message):
            """Zapisuje wiadomość do pliku log i wyświetla ją"""
            print(message)
            log_file.write(message + "\n")
            log_file.flush()  # Natychmiast zapisz do pliku
        
        log(f"=== Naprawa bazy danych {timestamp} ===\n")
        
        # Utwórz kopię zapasową bazy danych
        backup_filename = f"database_backup_{timestamp}.db"
        
        if os.path.exists("database.db"):
            import shutil
            shutil.copy2("database.db", backup_filename)
            log(f"Utworzono kopię zapasową bazy danych: {backup_filename}")
        else:
            log("ERROR: Plik bazy danych nie istnieje!")
            log_file.close()
            return False
        
        # Połącz z bazą danych
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        
        # 1. Sprawdź jakie tabele są w bazie danych
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        log(f"Tabele w bazie danych: {[t[0] for t in tables]}")
        
        # 2. Sprawdź strukturę tabeli shifts
        log("\nSprawdzam strukturę tabeli shifts:")
        
        cursor.execute("PRAGMA table_info(shifts)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        log("Aktualne kolumny:")
        for col in columns:
            log(f"   - {col[1]} ({col[2]}, default: {col[4]})")
        
        # 3. Sprawdź, czy brakujące kolumny istnieją
        missing_columns = []
        if "status" not in column_names:
            missing_columns.append("status")
        if "is_holiday" not in column_names:
            missing_columns.append("is_holiday")
        if "is_sick" not in column_names:
            missing_columns.append("is_sick")
        
        # 4. Dodaj brakujące kolumny
        if missing_columns:
            log(f"\nBrakujące kolumny: {missing_columns}")
            log("Dodaję brakujące kolumny...")
            
            try:
                # Utwórz tymczasową tabelę z nowymi kolumnami
                cursor.execute('''
                CREATE TABLE shifts_new (
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
                
                # Kopiuj dane ze starej tabeli do nowej
                existing_columns = ", ".join(column_names)
                log(f"Kopiowanie danych z kolumn: {existing_columns}")
                
                # Sprawdź liczbę rekordów przed transferem
                cursor.execute("SELECT COUNT(*) FROM shifts")
                count_before = cursor.fetchone()[0]
                log(f"Liczba rekordów przed transferem: {count_before}")
                
                # Wykonaj kopiowanie danych
                cursor.execute(f"INSERT INTO shifts_new ({existing_columns}) SELECT {existing_columns} FROM shifts")
                
                # Usuń starą tabelę i zmień nazwę nowej
                cursor.execute("DROP TABLE shifts")
                cursor.execute("ALTER TABLE shifts_new RENAME TO shifts")
                
                # Sprawdź liczbę rekordów po transferze
                cursor.execute("SELECT COUNT(*) FROM shifts")
                count_after = cursor.fetchone()[0]
                log(f"Liczba rekordów po transferze: {count_after}")
                
                # Zatwierdź zmiany
                conn.commit()
                log("Zmiany zatwierdzone.")
                
            except Exception as e:
                log(f"BŁĄD podczas dodawania kolumn: {e}")
                conn.rollback()
                
                # Spróbuj alternatywną metodę dodawania kolumn
                log("\nPróbuję alternatywną metodę...")
                try:
                    # Dodaj kolumny bezpośrednio
                    if "status" not in column_names:
                        cursor.execute("ALTER TABLE shifts ADD COLUMN status TEXT DEFAULT 'Obecny'")
                        log("Dodano kolumnę 'status'")
                    
                    if "is_holiday" not in column_names:
                        cursor.execute("ALTER TABLE shifts ADD COLUMN is_holiday BOOLEAN DEFAULT 0")
                        log("Dodano kolumnę 'is_holiday'")
                    
                    if "is_sick" not in column_names:
                        cursor.execute("ALTER TABLE shifts ADD COLUMN is_sick BOOLEAN DEFAULT 0")
                        log("Dodano kolumnę 'is_sick'")
                    
                    conn.commit()
                    log("Alternatywna metoda zakończona pomyślnie.")
                    
                except Exception as e2:
                    log(f"BŁĄD podczas alternatywnej metody: {e2}")
                    conn.rollback()
        else:
            log("\nWszystkie wymagane kolumny już istnieją.")
        
        # 5. Sprawdź strukturę tabeli po zmianach
        log("\nSprawdzam strukturę tabeli shifts po zmianach:")
        
        cursor.execute("PRAGMA table_info(shifts)")
        columns_after = cursor.fetchall()
        column_names_after = [col[1] for col in columns_after]
        
        log("Aktualne kolumny po zmianach:")
        for col in columns_after:
            log(f"   - {col[1]} ({col[2]}, default: {col[4]})")
        
        # 6. Sprawdź czy wszystkie wymagane kolumny zostały dodane
        required_columns = ["status", "is_holiday", "is_sick"]
        all_added = all(col in column_names_after for col in required_columns)
        
        if all_added:
            log("\nWszystkie wymagane kolumny zostały dodane pomyślnie!")
        else:
            missing = [col for col in required_columns if col not in column_names_after]
            log(f"\nUWAGA: Nadal brakuje kolumn: {missing}")
        
        # Zamknij połączenie i plik log
        conn.close()
        log(f"\nOperacja zakończona. Szczegóły w pliku: {log_filename}")
        log_file.close()
        
        return all_added
        
    except Exception as e:
        print(f"Wystąpił błąd podczas naprawy bazy danych: {e}")
        if 'log_file' in locals() and not log_file.closed:
            log_file.write(f"\nWystąpił krytyczny błąd: {e}\n")
            log_file.close()
        return False

if __name__ == "__main__":
    success = fix_database_full()
    print(f"Status naprawy: {'SUKCES' if success else 'NIEPOWODZENIE'}")
    sys.exit(0 if success else 1)
