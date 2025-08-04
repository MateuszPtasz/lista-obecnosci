import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

print("=== ATTENDANCE LOGS FOR USER 1111 ===")
cursor.execute("""
SELECT worker_id, start_time, stop_time, 
       strftime('%Y-%m-%d', start_time) as date,
       ROUND((julianday(stop_time) - julianday(start_time)) * 24, 2) as hours
FROM attendance_logs 
WHERE worker_id = '1111' 
ORDER BY start_time DESC 
LIMIT 20
""")

rows = cursor.fetchall()
for row in rows:
    print(f"{row[0]}: {row[3]} | {row[1]} -> {row[2]} | {row[4]}h")

print(f"\nTotal records: {len(rows)}")

# Sprawdź także wszystkie rekordy
cursor.execute("SELECT COUNT(*) FROM attendance_logs WHERE worker_id = '1111'")
total = cursor.fetchone()[0]
print(f"Total attendance records for 1111: {total}")

conn.close()
