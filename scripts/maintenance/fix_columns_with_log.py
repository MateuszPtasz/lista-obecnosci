import sqlite3
import os
import time

# Zapisz dane do pliku
log_file = "fix_status_" + time.strftime("%Y%m%d_%H%M%S") + ".txt"

with open(log_file, "w", encoding="utf-8") as f:
    # Opis operacji
    f.write("Dodawanie kolumn do tabeli shifts w bazie danych\n")
    f.write("=" * 50 + "\n\n")
    
    try:
        # Połączenie z bazą
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Pobranie informacji o strukturze tabeli przed zmianami
        cursor.execute("PRAGMA table_info(shifts)")
        columns_before = cursor.fetchall()
        
        f.write("Struktura tabeli przed zmianami:\n")
        for col in columns_before:
            f.write(f"  - {col[1]} ({col[2]}, default: {col[4]})\n")
        
        # Lista kolumn do dodania
        columns_to_add = [
            ("status", "TEXT", "'Obecny'"),
            ("is_holiday", "BOOLEAN", "0"),
            ("is_sick", "BOOLEAN", "0")
        ]
        
        # Dodawanie kolumn
        f.write("\nDodawanie kolumn:\n")
        for column_name, column_type, default_value in columns_to_add:
            # Sprawdź czy kolumna już istnieje
            column_exists = any(col[1] == column_name for col in columns_before)
            
            if not column_exists:
                try:
                    sql = f"ALTER TABLE shifts ADD COLUMN {column_name} {column_type} DEFAULT {default_value}"
                    f.write(f"  Dodawanie {column_name}: {sql}\n")
                    cursor.execute(sql)
                    f.write(f"  ✓ Dodano kolumnę {column_name}\n")
                except Exception as e:
                    f.write(f"  ✗ Błąd podczas dodawania kolumny {column_name}: {str(e)}\n")
            else:
                f.write(f"  ✓ Kolumna {column_name} już istnieje\n")
        
        # Zatwierdź zmiany
        conn.commit()
        
        # Pobranie informacji o strukturze tabeli po zmianach
        cursor.execute("PRAGMA table_info(shifts)")
        columns_after = cursor.fetchall()
        
        f.write("\nStruktura tabeli po zmianach:\n")
        for col in columns_after:
            f.write(f"  - {col[1]} ({col[2]}, default: {col[4]})\n")
        
        # Sprawdź czy wszystkie kolumny zostały dodane
        all_columns_exist = all(
            any(col[1] == column_name for col in columns_after)
            for column_name, _, _ in columns_to_add
        )
        
        if all_columns_exist:
            f.write("\n✓ SUKCES: Wszystkie kolumny zostały dodane lub już istniały\n")
        else:
            f.write("\n✗ BŁĄD: Nie wszystkie kolumny zostały dodane\n")
            
        # Zamknij połączenie z bazą
        conn.close()
        
    except Exception as e:
        f.write(f"\n✗ KRYTYCZNY BŁĄD: {str(e)}\n")

print(f"Operacja zakończona, wyniki zapisano w pliku: {log_file}")
