#!/usr/bin/env python3
import sqlite3

# Połącz z bazą danych
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

try:
    # Sprawdź jakie tabele istnieją
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("Tabele w bazie danych:")
    for table in tables:
        print(f"  - {table[0]}")
    
    # Sprawdź czy tabela employees istnieje
    if any('employees' in table[0] for table in tables):
        print("\nSprawdzam strukturę tabeli employees:")
        cursor.execute("PRAGMA table_info(employees)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # Sprawdź czy kolumna pin już istnieje
        column_names = [col[1] for col in columns]
        if 'pin' not in column_names:
            print("\nDodaję kolumnę PIN...")
            cursor.execute("ALTER TABLE employees ADD COLUMN pin TEXT")
            conn.commit()
            print("✅ Kolumna PIN została dodana!")
        else:
            print("✅ Kolumna PIN już istnieje")
    else:
        print("❌ Tabela employees nie istnieje")
        
except Exception as e:
    print(f"❌ Błąd: {e}")
    
finally:
    conn.close()
