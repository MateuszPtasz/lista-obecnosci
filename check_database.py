import sqlite3

def check_tables():
    try:
        # Połączenie z bazą danych
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Lista wszystkich tabel
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("Tabele w bazie danych:", [t[0] for t in tables])
        
        # Sprawdź strukturę tabeli shifts (jeśli istnieje)
        if ('shifts',) in tables:
            cursor.execute("PRAGMA table_info(shifts)")
            shifts_columns = cursor.fetchall()
            print("\nStruktura tabeli shifts:")
            for col in shifts_columns:
                print(f"  {col[1]} ({col[2]}) {'PRIMARY KEY' if col[5] else ''}")
            
            # Pokaż ostatnie rekordy w tabeli shifts
            cursor.execute("SELECT id, employee_id, start_time, stop_time FROM shifts ORDER BY start_time DESC LIMIT 5")
            shifts = cursor.fetchall()
            print("\nOstatnie 5 rekordów w tabeli shifts:")
            for shift in shifts:
                print(f"  ID: {shift[0]}, Pracownik: {shift[1]}, Start: {shift[2]}, Stop: {shift[3]}")
        
        # Sprawdź, czy są aktywne zmiany (pracownicy obecnie w pracy)
        cursor.execute("SELECT COUNT(*) FROM shifts WHERE stop_time IS NULL")
        active_count = cursor.fetchone()[0]
        print(f"\nLiczba aktywnych zmian (pracownicy obecnie w pracy): {active_count}")
        
        if active_count > 0:
            cursor.execute("""
                SELECT s.id, s.employee_id, e.name, s.start_time 
                FROM shifts s 
                JOIN employees e ON s.employee_id = e.id
                WHERE s.stop_time IS NULL
            """)
            active_shifts = cursor.fetchall()
            print("\nAktywne zmiany:")
            for shift in active_shifts:
                print(f"  ID: {shift[0]}, Pracownik: {shift[1]}, Nazwa: {shift[2]}, Start: {shift[3]}")
        
        # Sprawdź czy istnieje tabela pracowników i pokaż pierwszych 5
        if ('employees',) in tables:
            cursor.execute("PRAGMA table_info(employees)")
            employee_columns = cursor.fetchall()
            print("\nStruktura tabeli employees:")
            for col in employee_columns:
                print(f"  {col[1]} ({col[2]}) {'PRIMARY KEY' if col[5] else ''}")
            
            cursor.execute("SELECT id, name FROM employees LIMIT 5")
            employees = cursor.fetchall()
            print("\nPierwszych 5 pracowników:")
            for employee in employees:
                print(f"  ID: {employee[0]}, Nazwa: {employee[1]}")
        
        conn.close()
        
    except Exception as e:
        print(f"Błąd podczas sprawdzania bazy danych: {e}")

if __name__ == "__main__":
    check_tables()
