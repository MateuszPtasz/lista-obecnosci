#!/usr/bin/env python
# fix_active_sessions.py - skrypt do naprawy problemów z aktywnymi sesjami pracowników

import sys
import os
import datetime as dt
import sqlite3
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect
from database import Base, get_db, engine

# Importy do tabeli shifts
try:
    import models
except ImportError:
    print("Błąd: Nie można zaimportować modułu models.")
    sys.exit(1)

# Sprawdź, czy tabela admin_logs istnieje, a jeśli nie, utwórz ją
def ensure_admin_logs_table():
    inspector = inspect(engine)
    if 'admin_logs' not in inspector.get_table_names():
        print("Tabela admin_logs nie istnieje - tworzenie tabeli...")
        Base.metadata.create_all(bind=engine, tables=[models.AdminLog.__table__])
        print("Tabela admin_logs została utworzona.")
    else:
        print("Tabela admin_logs już istnieje.")

def main():
    print("Skrypt do naprawy aktywnych sesji pracowników")
    print("=" * 50)
    
    # Upewnij się, że tabela admin_logs istnieje
    ensure_admin_logs_table()
    
    # Połączenie z bazą danych
    db = next(get_db())
    
    try:
        # Pobierz wszystkich pracowników z aktywnymi zmianami
        active_shifts = db.query(models.Shift).filter(
            models.Shift.stop_time == None
        ).all()
        
        print(f"Znaleziono {len(active_shifts)} aktywnych zmian.")
        
        if not active_shifts:
            print("Nie znaleziono aktywnych zmian do naprawy.")
            return
        
        print("\nLista aktywnych zmian:")
        for i, shift in enumerate(active_shifts, 1):
            # Pobierz informacje o pracowniku
            employee = db.query(models.Employee).filter(
                models.Employee.id == shift.employee_id
            ).first()
            
            employee_name = employee.name if employee else "Nieznany pracownik"
            
            # Oblicz czas trwania zmiany
            duration = dt.datetime.now() - shift.start_time
            duration_hours = duration.total_seconds() // 3600
            
            print(f"{i}. ID: {shift.id}, Pracownik: {shift.employee_id} ({employee_name})")
            print(f"   Rozpoczęcie: {shift.start_time}")
            print(f"   Czas trwania: {duration_hours:.1f} godz.")
            print(f"   Lokalizacja: {shift.start_location}")
            print("-" * 40)
        
        # Zapytaj użytkownika, które zmiany chce naprawić
        while True:
            choice = input("\nWybierz opcję:\n1. Zakończ jedną zmianę\n2. Zakończ wszystkie zmiany\n3. Wyjdź\nTwój wybór: ")
            
            if choice == "1":
                # Zakończ jedną zmianę
                shift_id = input("Podaj numer zmiany do zakończenia: ")
                try:
                    shift_index = int(shift_id) - 1
                    if 0 <= shift_index < len(active_shifts):
                        shift = active_shifts[shift_index]
                        stop_time = dt.datetime.now()
                        shift.stop_time = stop_time
                        shift.stop_location = "Naprawiono przez skrypt fix_active_sessions.py"
                        
                        # Oblicz czas trwania
                        duration = stop_time - shift.start_time
                        duration_minutes = int(duration.total_seconds() // 60)
                        shift.duration_min = duration_minutes
                        
                        # Dodaj log administratora
                        try:
                            admin_log = models.AdminLog(
                                action_type="FORCE_STOP",
                                admin_id="system",
                                target_id=str(shift.employee_id),
                                notes=f"Naprawiono przez skrypt fix_active_sessions.py. Shift ID: {shift.id}, Duration: {duration_minutes} min"
                            )
                            
                            db.add(admin_log)
                        except Exception as log_error:
                            print(f"Ostrzeżenie: Nie udało się dodać logu administracyjnego: {log_error}")
                        
                        db.commit()
                        
                        print(f"Pomyślnie zakończono zmianę {shift_id}.")
                    else:
                        print("Nieprawidłowy numer zmiany.")
                except ValueError:
                    print("Wprowadź prawidłowy numer zmiany.")
            
            elif choice == "2":
                # Zakończ wszystkie zmiany
                confirm = input("Czy na pewno chcesz zakończyć WSZYSTKIE aktywne zmiany? (tak/nie): ")
                if confirm.lower() == "tak":
                    stop_time = dt.datetime.now()
                    count = 0
                    
                    for shift in active_shifts:
                        shift.stop_time = stop_time
                        shift.stop_location = "Masowe zakończenie przez skrypt fix_active_sessions.py"
                        
                        # Oblicz czas trwania
                        duration = stop_time - shift.start_time
                        duration_minutes = int(duration.total_seconds() // 60)
                        shift.duration_min = duration_minutes
                        
                        # Dodaj log administratora
                        try:
                            admin_log = models.AdminLog(
                                action_type="FORCE_STOP",
                                admin_id="system",
                                target_id=str(shift.employee_id),
                                notes=f"Masowe zakończenie przez skrypt fix_active_sessions.py. Shift ID: {shift.id}, Duration: {duration_minutes} min"
                            )
                            
                            db.add(admin_log)
                        except Exception as log_error:
                            print(f"Ostrzeżenie: Nie udało się dodać logu administracyjnego: {log_error}")
                        
                        count += 1
                    
                    db.commit()
                    print(f"Pomyślnie zakończono {count} zmian.")
                else:
                    print("Anulowano operację.")
            
            elif choice == "3":
                print("Wychodzenie z programu...")
                break
            
            else:
                print("Nieprawidłowy wybór.")
    
    except Exception as e:
        print(f"Wystąpił błąd: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
