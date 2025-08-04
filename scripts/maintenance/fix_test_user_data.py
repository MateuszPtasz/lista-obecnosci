import sqlite3
import sys

def fix_corrupted_data():
    """Usuwa błędny rekord z bazą danych dla użytkownika testowego"""
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        print("=== ANALIZA REKORDÓW UŻYTKOWNIKA '1111' ===")
        
        # Sprawdź wszystkie rekordy
        cursor.execute("""
            SELECT 
                id,
                worker_id,
                start_time,
                stop_time,
                CASE 
                    WHEN stop_time IS NOT NULL AND start_time IS NOT NULL THEN
                        ROUND((julianday(stop_time) - julianday(start_time)) * 24, 2)
                    ELSE NULL
                END as hours,
                DATE(start_time) as date
            FROM attendance_logs 
            WHERE worker_id = '1111'
            ORDER BY start_time DESC
        """)
        
        records = cursor.fetchall()
        print(f"Znaleziono {len(records)} rekordów:")
        print()
        
        corrupted_records = []
        for i, record in enumerate(records, 1):
            record_id, worker_id, start_time, stop_time, hours, date = record
            print(f"{i}. ID: {record_id}, Data: {date}, Godziny: {hours}h, Start: {start_time}, Stop: {stop_time}")
            
            # Identyfikuj podejrzane rekordy (>24 godziny)
            if hours and hours > 24:
                corrupted_records.append(record)
                print(f"   ⚠️  PODEJRZANY REKORD - {hours} godzin!")
        
        print(f"\n=== ZNALEZIONO {len(corrupted_records)} PODEJRZANYCH REKORDÓW ===")
        
        if corrupted_records:
            for record in corrupted_records:
                record_id, worker_id, start_time, stop_time, hours, date = record
                print(f"Błędny rekord ID {record_id}: {date} - {hours}h ({start_time} do {stop_time})")
            
            response = input("\nCzy usunąć te błędne rekordy? (tak/nie): ").lower().strip()
            
            if response in ['tak', 't', 'yes', 'y']:
                for record in corrupted_records:
                    record_id, worker_id, start_time, stop_time, hours, date = record
                    
                    cursor.execute("""
                        DELETE FROM attendance_logs 
                        WHERE id = ?
                    """, (record_id,))
                    
                    print(f"✅ Usunięto rekord ID {record_id}: {date} - {hours}h")
                
                conn.commit()
                print(f"\n✅ Usunięto {len(corrupted_records)} błędnych rekordów")
                
                # Sprawdź statystyki po usunięciu
                print("\n=== STATYSTYKI PO NAPRAWIE ===")
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_shifts,
                        SUM(CASE 
                            WHEN stop_time IS NOT NULL AND start_time IS NOT NULL THEN
                                ROUND((julianday(stop_time) - julianday(start_time)) * 24, 2)
                            ELSE 0
                        END) as total_hours,
                        AVG(CASE 
                            WHEN stop_time IS NOT NULL AND start_time IS NOT NULL THEN
                                ROUND((julianday(stop_time) - julianday(start_time)) * 24, 2)
                            ELSE NULL
                        END) as avg_hours,
                        MIN(DATE(start_time)) as first_date,
                        MAX(DATE(start_time)) as last_date
                    FROM attendance_logs 
                    WHERE worker_id = '1111'
                """)
                
                stats = cursor.fetchone()
                if stats[0] > 0:
                    total_shifts, total_hours, avg_hours, first_date, last_date = stats
                    print(f"Liczba zmian: {total_shifts}")
                    print(f"Łączne godziny: {total_hours:.2f}h")
                    print(f"Średnia godzin/zmiana: {avg_hours:.2f}h") 
                    print(f"Okres: {first_date} - {last_date}")
                else:
                    print("Brak rekordów po naprawie")
            else:
                print("Anulowano usuwanie")
        else:
            print("Nie znaleziono błędnych rekordów (>24h)")
            
    except Exception as e:
        print(f"❌ Błąd: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    fix_corrupted_data()
