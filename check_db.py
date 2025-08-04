import sqlite3

def check_database():
    """Sprawdź zawartość bazy danych"""
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Sprawdź wszystkie tabele
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table'
        """)
        
        tables = cursor.fetchall()
        print("📋 Tabele w bazie danych:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Sprawdź czy device_logs istnieje
        if any('device_logs' in table for table in tables):
            print("\n✅ Tabela device_logs istnieje")
            
            cursor.execute("PRAGMA table_info(device_logs)")
            columns = cursor.fetchall()
            print("\n📋 Struktura tabeli device_logs:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
        else:
            print("\n❌ Tabela device_logs nie istnieje")
            print("🔧 Próba utworzenia tabeli...")
            
            # Utwórz tabelę ręcznie
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS device_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    worker_id VARCHAR(50) NOT NULL,
                    device_id VARCHAR(255) NOT NULL,
                    device_model VARCHAR(255),
                    os_version VARCHAR(100),
                    app_version VARCHAR(50),
                    location VARCHAR(255),
                    is_approved BOOLEAN DEFAULT FALSE,
                    is_suspicious BOOLEAN DEFAULT FALSE,
                    user_rejected BOOLEAN DEFAULT FALSE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            print("✅ Tabela device_logs została utworzona")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Błąd: {e}")

if __name__ == "__main__":
    check_database()
