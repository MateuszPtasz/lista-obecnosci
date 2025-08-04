import sqlite3
import os

# Utwórz plik z informacjami o bazie danych
with open("db_structure.txt", "w", encoding="utf-8") as f:
    f.write("=== STRUKTURA BAZY DANYCH ===\n\n")
    
    # Połącz z bazą danych
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    # Pobierz listę tabel
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    f.write(f"Tabele w bazie danych: {[t[0] for t in tables]}\n\n")
    
    # Sprawdź strukturę każdej tabeli
    for table in tables:
        table_name = table[0]
        f.write(f"Tabela: {table_name}\n")
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        for col in columns:
            f.write(f"   - {col[1]} ({col[2]}, default: {col[4]})\n")
        
        # Policz rekordy
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        f.write(f"   Liczba rekordów: {count}\n\n")
    
    # Zamknij połączenie
    conn.close()

print("Utworzono plik db_structure.txt z informacjami o bazie danych.")
