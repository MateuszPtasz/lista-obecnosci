# check_db_structure.py
import sqlite3

def check_database():
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        print("📊 Tabele w bazie danych:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        if not tables:
            print("   ❌ Brak tabel w bazie danych!")
            conn.close()
            return
        
        for table in tables:
            table_name = table[0]
            print(f"\n🗂️ Tabela: {table_name}")
            
            # Pokaż strukturę tabeli
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            for col in columns:
                print(f"   - {col[1]} ({col[2]})")
            
            # Pokaż liczbę rekordów
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   📊 Liczba rekordów: {count}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Błąd: {e}")

if __name__ == "__main__":
    check_database()
