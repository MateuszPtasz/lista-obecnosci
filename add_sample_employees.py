# add_sample_employees.py
"""
Dodaje przykładowych pracowników z ID zawierającymi litery i PIN-ami
"""

import sqlite3
from datetime import datetime

def add_sample_employees():
    """Dodaj przykładowych pracowników"""
    
    sample_employees = [
        {
            'id': 'JAN001',
            'name': 'Jan Kowalski', 
            'pin': '1234',
            'hourly_rate': 25.0,
            'rate_saturday': 30.0,
            'rate_sunday': 35.0,
            'rate_night': 28.0,
            'rate_overtime': 30.0
        },
        {
            'id': 'ANN002',
            'name': 'Anna Nowak',
            'pin': '5678', 
            'hourly_rate': 22.0,
            'rate_saturday': 27.0,
            'rate_sunday': 32.0,
            'rate_night': 25.0,
            'rate_overtime': 27.0
        },
        {
            'id': 'PIE003',
            'name': 'Piotr Wiśniewski',
            'pin': '9876',
            'hourly_rate': 28.0,
            'rate_saturday': 33.0,
            'rate_sunday': 38.0,
            'rate_night': 31.0,
            'rate_overtime': 33.0
        },
        {
            'id': '1111',  # Stary format numeryczny
            'name': 'Tomasz Testowy',
            'pin': '1111',
            'hourly_rate': 20.0,
            'rate_saturday': 25.0,
            'rate_sunday': 30.0,
            'rate_night': 23.0,
            'rate_overtime': 25.0
        },
        {
            'id': 'MAR004',
            'name': 'Maria Kowalczyk',
            'pin': '4321',
            'hourly_rate': 24.0,
            'rate_saturday': 29.0,
            'rate_sunday': 34.0,
            'rate_night': 27.0,
            'rate_overtime': 29.0
        }
    ]
    
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        print("👥 Dodaję przykładowych pracowników...")
        
        for emp in sample_employees:
            # Sprawdź czy pracownik już istnieje
            cursor.execute("SELECT id FROM employees WHERE id = ?", (emp['id'],))
            if cursor.fetchone():
                print(f"   ⚠️ Pracownik {emp['id']} już istnieje - pomijam")
                continue
            
            # Dodaj pracownika
            cursor.execute("""
                INSERT INTO employees (id, name, pin, hourly_rate, rate_saturday, rate_sunday, rate_night, rate_overtime)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                emp['id'], emp['name'], emp['pin'], emp['hourly_rate'],
                emp['rate_saturday'], emp['rate_sunday'], emp['rate_night'], emp['rate_overtime']
            ))
            
            print(f"   ✅ Dodano: {emp['id']} - {emp['name']} (PIN: {emp['pin']})")
        
        conn.commit()
        
        # Pokaż wszystkich pracowników
        print(f"\n📋 Lista wszystkich pracowników:")
        cursor.execute("SELECT id, name, pin, hourly_rate FROM employees ORDER BY id")
        employees = cursor.fetchall()
        
        for emp in employees:
            print(f"   ID: {emp[0]:<6} | Nazwa: {emp[1]:<20} | PIN: {emp[2]} | Stawka: {emp[3]}")
        
        print(f"\n✅ Dodano {len(sample_employees)} pracowników!")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Błąd: {e}")
        return False

if __name__ == "__main__":
    add_sample_employees()
