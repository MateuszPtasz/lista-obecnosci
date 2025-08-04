#!/usr/bin/env python3
# optimize_db_connections.py
# Skrypt do optymalizacji polaczen z baza danych i rozwiazania problemow z wydajnoscia

import os
import shutil
import sqlite3
import subprocess
import datetime
import sys

print("Sprawdzanie dzialajacych instancji aplikacji...")

# Sprawdzenie czy proces Python jest uruchomiony
try:
    if os.name == 'nt':  # Windows
        # Sprawdz czy proces main.py jest uruchomiony
        result = subprocess.run(["powershell", "Get-Process python | Where-Object { $_.CommandLine -like '*main.py*' }"], 
                               capture_output=True, text=True)
        if "python" in result.stdout.lower():
            print("Znaleziono dzialajace procesy aplikacji. Zatrzymywanie...")
            subprocess.run(["powershell", "Get-Process python | Where-Object { $_.CommandLine -like '*main.py*' } | Stop-Process -Force"], 
                          capture_output=True)
    else:  # Linux/Mac
        result = subprocess.run(["pgrep", "-f", "main.py"], capture_output=True, text=True)
        if result.stdout:
            print("Znaleziono dzialajace procesy aplikacji. Zatrzymywanie...")
            subprocess.run(["pkill", "-f", "main.py"])

except Exception as e:
    print(f"Blad podczas sprawdzania procesow: {str(e)}")

# Optymalizacja bazy danych SQLite
print("Optymalizacja bazy danych SQLite...")
database_path = "database.db"
if os.path.exists(database_path):
    print("Wykonywanie kopii zapasowej bazy danych...")
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_file = f"database_backup_{timestamp}.db"
    shutil.copy2(database_path, backup_file)
    
    try:
        print("Wykonywanie VACUUM na bazie danych...")
        conn = sqlite3.connect(database_path)
        conn.execute("VACUUM;")
        conn.execute("PRAGMA optimize;")
        conn.execute("PRAGMA integrity_check;")
        conn.close()
        print("Optymalizacja bazy danych ukonczona.")
    except Exception as e:
        print(f"Blad podczas optymalizacji bazy danych: {str(e)}")
else:
    print(f"Nie znaleziono pliku bazy danych: {database_path}")

# Czyszczenie zbednych plikow
print("Czyszczenie plikow tymczasowych i cache...")
folders_to_clean = ["__pycache__"]

for folder in folders_to_clean:
    if os.path.exists(folder):
        print(f"Czyszczenie folderu: {folder}")
        try:
            for root, dirs, files in os.walk(folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        os.remove(file_path)
                        print(f"Usunięto: {file_path}")
                    except Exception as e:
                        print(f"Nie można usunąć {file_path}: {str(e)}")
        except Exception as e:
            print(f"Błąd podczas czyszczenia folderu {folder}: {str(e)}")

# Sprawdz konflikty rozszerzen VS Code
print("Sprawdzanie potencjalnych konfliktów rozszerzen VS Code...")
print("Sugerowane akcje:")
print("1. Tymczasowo wylacz nieuzywane rozszerzenia VS Code")
print("2. Uruchom VS Code w trybie bezpiecznym (--disable-extensions)")
print("3. Zmniejsz liczbę otwartych plików i kart")
print("4. Upewnij sie, ze system ma wystarczajaca ilosc dostepnej pamieci RAM")

print("Optymalizacja zakonczona. Zalecamy ponowne uruchomienie aplikacji.")
