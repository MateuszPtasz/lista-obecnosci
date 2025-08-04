#!/usr/bin/env python3
"""Sprawdź jakich pracowników mamy w bazie"""

import sqlite3

def check_employees():
    """Sprawdź listę pracowników w bazie danych"""
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name, pin FROM employees")
        employees = cursor.fetchall()
        
        print("=== Pracownicy w bazie danych ===")
        if employees:
            for emp in employees:
                print(f"ID: {emp[0]}, Nazwa: {emp[1]}, PIN: {emp[2]}")
        else:
            print("Brak pracowników w bazie danych!")
            
        conn.close()
        
    except Exception as e:
        print(f"Błąd: {e}")

if __name__ == "__main__":
    check_employees()
