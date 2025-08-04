import sqlite3
from datetime import datetime

def check_database():
    """Sprawdzenie stanu bazy danych"""
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    
    # 1. Sprawdź aktywne zmiany
    cur.execute('''
        SELECT s.id, s.employee_id, s.start_time, s.stop_time, e.name
        FROM shifts s
        LEFT JOIN employees e ON s.employee_id = e.id
        WHERE s.stop_time IS NULL
    ''')
    
    active_shifts = cur.fetchall()
    print("=== AKTYWNE ZMIANY ===")
    print(f"Liczba aktywnych zmian: {len(active_shifts)}")
    for shift in active_shifts:
        print(f"ID: {shift[0]}, Pracownik: {shift[1]} ({shift[4] or 'Brak nazwy'}), Start: {shift[2]}")
    print()
    
    # 2. Sprawdź czy wszystkie aktywne zmiany mają odpowiadających pracowników
    print("=== SPRAWDZANIE SPÓJNOŚCI DANYCH ===")
    for shift in active_shifts:
        employee_id = shift[1]
        cur.execute('SELECT id, name FROM employees WHERE id = ?', (employee_id,))
        employee = cur.fetchone()
        if employee:
            print(f"OK: Pracownik {employee_id} ({employee[1]}) istnieje w bazie")
        else:
            print(f"BŁĄD: Pracownik {employee_id} nie istnieje w bazie!")
    print()
    
    # 3. Wypisz wszystkich pracowników
    cur.execute('SELECT id, name, pin FROM employees')
    employees = cur.fetchall()
    print("=== LISTA PRACOWNIKÓW ===")
    print(f"Liczba pracowników: {len(employees)}")
    for emp in employees:
        cur.execute('SELECT COUNT(*) FROM shifts WHERE employee_id = ? AND stop_time IS NULL', (emp[0],))
        active_count = cur.fetchone()[0]
        status = "AKTYWNY" if active_count > 0 else "nieaktywny"
        print(f"ID: {emp[0]}, Nazwa: {emp[1]}, PIN: {emp[2]}, Status: {status}")
    
    conn.close()

if __name__ == '__main__':
    print(f"Sprawdzanie bazy danych - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    check_database()
