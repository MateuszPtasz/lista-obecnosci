import sqlite3
from datetime import datetime

# Sprawdź aktywne sesje
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

print("=== AKTYWNE SESJE ===")
cursor.execute('SELECT worker_id, start_time, stop_time FROM attendance_logs WHERE stop_time IS NULL')
active = cursor.fetchall()
for row in active:
    print(f"Pracownik: {row[0]}, Start: {row[1]}, Stop: {row[2]}")

if active:
    print(f"\nZakańczam {len(active)} aktywnych sesji...")
    cursor.execute('UPDATE attendance_logs SET stop_time = ? WHERE stop_time IS NULL', (datetime.now(),))
    conn.commit()
    print("✅ Sesje zakończone")
else:
    print("✅ Brak aktywnych sesji")

print("\n=== OSTATNIE 5 SESJI ===")
cursor.execute('SELECT worker_id, start_time, stop_time FROM attendance_logs ORDER BY id DESC LIMIT 5')
recent = cursor.fetchall()
for row in recent:
    print(f"Pracownik: {row[0]}, Start: {row[1]}, Stop: {row[2]}")

conn.close()
