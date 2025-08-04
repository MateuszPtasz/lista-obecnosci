# migration_add_pin.py
"""
Migracja bazy danych - dodanie pola PIN do tabeli employees
i zmiana ID na typ STRING (akceptuje litery)
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    db_path = "database.db"
    backup_path = f"database_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    
    print(f"🔄 Rozpoczynam migrację bazy danych...")
    
    # Sprawdź czy baza istnieje
    if not os.path.exists(db_path):
        print(f"❌ Plik bazy danych {db_path} nie istnieje!")
        return False
    
    try:
        # Utwórz kopię zapasową
        print(f"💾 Tworzę kopię zapasową: {backup_path}")
        import shutil
        shutil.copy2(db_path, backup_path)
        
        # Połącz z bazą danych
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Sprawdź aktualną strukturę tabeli employees
        cursor.execute("PRAGMA table_info(employees)")
        columns = cursor.fetchall()
        print(f"📋 Aktualna struktura tabeli employees:")
        for col in columns:
            print(f"   - {col[1]} ({col[2]})")
        
        # Sprawdź czy kolumna PIN już istnieje
        column_names = [col[1] for col in columns]
        if 'pin' not in column_names:
            print(f"➕ Dodaję kolumnę PIN...")
            cursor.execute("ALTER TABLE employees ADD COLUMN pin TEXT")
            
            # Ustaw domyślne PIN-y dla istniejących pracowników
            cursor.execute("SELECT id FROM employees")
            existing_employees = cursor.fetchall()
            
            for emp in existing_employees:
                emp_id = emp[0]
                # Generuj PIN na podstawie ID (ostatnie 4 cyfry lub uzupełnij zerami)
                if emp_id.isdigit():
                    pin = emp_id[-4:].zfill(4)
                else:
                    # Dla ID zawierających litery, użyj hash
                    pin = str(hash(emp_id) % 10000).zfill(4)
                
                cursor.execute("UPDATE employees SET pin = ? WHERE id = ?", (pin, emp_id))
                print(f"   📌 Pracownik {emp_id}: PIN = {pin}")
            
            print(f"✅ Kolumna PIN została dodana")
        else:
            print(f"ℹ️ Kolumna PIN już istnieje")
        
        # Sprawdź czy są jakieś dane do zaktualizowania
        cursor.execute("SELECT COUNT(*) FROM employees WHERE pin IS NULL OR pin = ''")
        null_pins = cursor.fetchone()[0]
        
        if null_pins > 0:
            print(f"🔧 Naprawiam {null_pins} pustych PIN-ów...")
            cursor.execute("SELECT id FROM employees WHERE pin IS NULL OR pin = ''")
            employees_without_pin = cursor.fetchall()
            
            for emp in employees_without_pin:
                emp_id = emp[0]
                if emp_id.isdigit():
                    pin = emp_id[-4:].zfill(4)
                else:
                    pin = str(hash(emp_id) % 10000).zfill(4)
                
                cursor.execute("UPDATE employees SET pin = ? WHERE id = ?", (pin, emp_id))
                print(f"   🔧 Pracownik {emp_id}: PIN = {pin}")
        
        # Zapisz zmiany
        conn.commit()
        
        # Sprawdź finalną strukturę
        print(f"\n📊 Finalna struktura tabeli employees:")
        cursor.execute("PRAGMA table_info(employees)")
        final_columns = cursor.fetchall()
        for col in final_columns:
            print(f"   - {col[1]} ({col[2]})")
        
        # Pokaż przykładowe dane
        print(f"\n👥 Przykładowi pracownicy:")
        cursor.execute("SELECT id, name, pin FROM employees LIMIT 5")
        sample_employees = cursor.fetchall()
        for emp in sample_employees:
            print(f"   ID: {emp[0]}, Nazwa: {emp[1]}, PIN: {emp[2]}")
        
        conn.close()
        print(f"\n✅ Migracja zakończona pomyślnie!")
        print(f"💾 Kopia zapasowa: {backup_path}")
        return True
        
    except Exception as e:
        print(f"❌ Błąd podczas migracji: {e}")
        return False

if __name__ == "__main__":
    migrate_database()
