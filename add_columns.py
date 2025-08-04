import sqlite3

# Połącz z bazą danych
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

try:
    # Dodaj kolumny do tabeli shifts
    cursor.execute("ALTER TABLE shifts ADD COLUMN status TEXT DEFAULT 'Obecny'")
    cursor.execute("ALTER TABLE shifts ADD COLUMN is_holiday BOOLEAN DEFAULT 0")
    cursor.execute("ALTER TABLE shifts ADD COLUMN is_sick BOOLEAN DEFAULT 0")
    
    # Zatwierdź zmiany
    conn.commit()
    
    print("Kolumny zostały dodane!")
    
except sqlite3.OperationalError as e:
    # Ignoruj błąd, jeśli kolumny już istnieją
    print(f"Błąd: {e}")
    
finally:
    # Zamknij połączenie
    conn.close()
