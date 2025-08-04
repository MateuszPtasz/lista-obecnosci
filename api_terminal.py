#!/usr/bin/env python
# api_terminal.py - Terminal API do diagnostyki i zarządzania systemem

import sys
import os
import argparse
import subprocess
import json
import datetime as dt
from database import get_db
from sqlalchemy import text

def print_header(title):
    """Wyświetla sformatowany nagłówek"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def show_menu():
    """Wyświetla główne menu"""
    print_header("TERMINAL DIAGNOSTYCZNY SYSTEMU LISTA OBECNOŚCI")
    print("""
1. Zarządzanie sesjami
2. Informacje systemowe
3. Diagnostyka połączenia
4. Narzędzia naprawcze
5. Wyjście
""")
    return input("Wybierz opcję: ")

def sessions_menu():
    """Menu zarządzania sesjami"""
    print_header("ZARZĄDZANIE SESJAMI PRACOWNIKÓW")
    print("""
1. Lista aktywnych sesji
2. Zakończ sesję pracownika
3. Zakończ wszystkie sesje
4. Powrót
""")
    return input("Wybierz opcję: ")

def system_info_menu():
    """Menu informacji systemowych"""
    print_header("INFORMACJE SYSTEMOWE")
    print("""
1. Status serwerów
2. Liczba rekordów w tabelach
3. Informacje o środowisku
4. Powrót
""")
    return input("Wybierz opcję: ")

def repair_tools_menu():
    """Menu narzędzi naprawczych"""
    print_header("NARZĘDZIA NAPRAWCZE")
    print("""
1. Napraw aktywne sesje
2. Sprawdź integralność bazy danych
3. Uruchom ponownie serwery API
4. Powrót
""")
    return input("Wybierz opcję: ")

def list_active_sessions():
    """Wyświetla listę aktywnych sesji pracowników"""
    try:
        db = next(get_db())
        result = db.execute(text("""
            SELECT s.id, s.employee_id, e.name, s.start_time, s.start_location
            FROM shifts s
            LEFT JOIN employees e ON s.employee_id = e.id
            WHERE s.stop_time IS NULL
            ORDER BY s.start_time
        """))
        
        sessions = result.fetchall()
        
        print_header(f"AKTYWNE SESJE PRACOWNIKÓW: {len(sessions)}")
        
        if not sessions:
            print("Brak aktywnych sesji pracowników.")
            return
        
        now = dt.datetime.now()
        
        print(f"{'ID':5} {'Pracownik ID':12} {'Imię i nazwisko':30} {'Rozpoczęcie':20} {'Czas trwania':15}")
        print("-" * 90)
        
        for session in sessions:
            start_time = session[3]
            duration = now - start_time
            hours = int(duration.total_seconds() // 3600)
            minutes = int((duration.total_seconds() % 3600) // 60)
            duration_str = f"{hours}h {minutes}min"
            
            print(f"{session[0]:5} {session[1]:12} {(session[2] or 'Nieznany'):30} {start_time.strftime('%Y-%m-%d %H:%M'):20} {duration_str:15}")
    
    except Exception as e:
        print(f"\n❌ Błąd podczas listowania sesji: {e}")
    finally:
        db.close()
        
    input("\nNaciśnij Enter, aby kontynuować...")

def end_session(all_sessions=False):
    """Kończy sesję pracownika lub wszystkie sesje"""
    try:
        db = next(get_db())
        
        if all_sessions:
            # Potwierdzenie zakończenia wszystkich sesji
            confirm = input("\n⚠️ Czy na pewno chcesz zakończyć WSZYSTKIE aktywne sesje? (tak/nie): ")
            if confirm.lower() != "tak":
                print("Anulowano operację.")
                return
            
            # Pobierz liczbę aktywnych sesji
            count = db.execute(text("SELECT COUNT(*) FROM shifts WHERE stop_time IS NULL")).scalar()
            
            if count == 0:
                print("Brak aktywnych sesji do zakończenia.")
                return
            
            # Zakończ wszystkie sesje
            now = dt.datetime.now()
            db.execute(text("""
                UPDATE shifts
                SET stop_time = :now,
                    stop_location = 'Zakończono przez terminal diagnostyczny',
                    duration_min = CAST((julianday(:now) - julianday(start_time)) * 24 * 60 AS INTEGER)
                WHERE stop_time IS NULL
            """), {"now": now})
            
            # Dodaj log administratora dla każdej zakończonej sesji
            active_workers = db.execute(text("""
                SELECT employee_id FROM shifts 
                WHERE stop_time = :now
            """), {"now": now}).fetchall()
            
            for worker in active_workers:
                db.execute(text("""
                    INSERT INTO admin_logs (action_type, admin_id, target_id, action_time, notes)
                    VALUES ('FORCE_STOP', 'admin_terminal', :target_id, :action_time, 'Masowe zakończenie przez terminal diagnostyczny')
                """), {
                    "target_id": str(worker[0]),
                    "action_time": now
                })
            
            db.commit()
            print(f"\n✅ Pomyślnie zakończono {count} aktywnych sesji.")
        
        else:
            # Wyświetl listę aktywnych sesji
            list_active_sessions()
            
            session_id = input("\nPodaj ID sesji do zakończenia (lub 'q' aby anulować): ")
            
            if session_id.lower() == 'q':
                return
            
            try:
                session_id = int(session_id)
            except ValueError:
                print("Nieprawidłowe ID sesji.")
                return
            
            # Sprawdź czy sesja istnieje i jest aktywna
            employee = db.execute(text("""
                SELECT e.id, e.name FROM shifts s
                LEFT JOIN employees e ON s.employee_id = e.id
                WHERE s.id = :session_id AND s.stop_time IS NULL
            """), {"session_id": session_id}).fetchone()
            
            if not employee:
                print(f"Nie znaleziono aktywnej sesji o ID {session_id}.")
                return
            
            # Zakończ sesję
            now = dt.datetime.now()
            db.execute(text("""
                UPDATE shifts
                SET stop_time = :now,
                    stop_location = 'Zakończono przez terminal diagnostyczny',
                    duration_min = CAST((julianday(:now) - julianday(start_time)) * 24 * 60 AS INTEGER)
                WHERE id = :session_id AND stop_time IS NULL
            """), {"now": now, "session_id": session_id})
            
            # Dodaj log administratora
            db.execute(text("""
                INSERT INTO admin_logs (action_type, admin_id, target_id, action_time, notes)
                VALUES ('FORCE_STOP', 'admin_terminal', :target_id, :action_time, 'Zakończono przez terminal diagnostyczny')
            """), {
                "target_id": str(employee[0]),
                "action_time": now
            })
            
            db.commit()
            print(f"\n✅ Pomyślnie zakończono sesję pracownika: {employee[1]} (ID: {employee[0]})")
    
    except Exception as e:
        print(f"\n❌ Błąd podczas zakończania sesji: {e}")
        db.rollback()
    finally:
        db.close()
    
    input("\nNaciśnij Enter, aby kontynuować...")

def check_database_tables():
    """Wyświetla liczbę rekordów w poszczególnych tabelach"""
    try:
        db = next(get_db())
        
        tables = [
            "employees", "shifts", "admin_logs", "users", "pin_access_logs"
        ]
        
        print_header("LICZBA REKORDÓW W TABELACH")
        
        for table in tables:
            try:
                count = db.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                print(f"{table:20} {count:8} rekordów")
            except Exception as e:
                print(f"{table:20} ❌ Błąd: {str(e)[:50]}")
        
    except Exception as e:
        print(f"\n❌ Błąd podczas sprawdzania tabel: {e}")
    finally:
        db.close()
    
    input("\nNaciśnij Enter, aby kontynuować...")

def check_server_status():
    """Sprawdza status serwerów API"""
    print_header("STATUS SERWERÓW API")
    
    servers = [
        {"name": "Główny serwer API", "url": "http://127.0.0.1:8000/api/health"},
        {"name": "Zapasowy serwer API", "url": "http://127.0.0.1:8002/api/health"},
        {"name": "Alternatywny serwer API", "url": "http://127.0.0.1:8080/api/health"}
    ]
    
    for server in servers:
        try:
            import requests
            response = requests.get(server["url"], timeout=2)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    status = data.get("status", "Nieznany")
                    uptime = data.get("uptime", "Nieznany")
                    print(f"{server['name']:25} ✅ Online (Status: {status}, Uptime: {uptime})")
                except:
                    print(f"{server['name']:25} ✅ Online (Odpowiedź: {response.status_code})")
            else:
                print(f"{server['name']:25} ⚠️ Odpowiedź: {response.status_code}")
                
        except requests.exceptions.RequestException:
            print(f"{server['name']:25} ❌ Niedostępny")
        except Exception as e:
            print(f"{server['name']:25} ❌ Błąd: {str(e)[:50]}")
    
    input("\nNaciśnij Enter, aby kontynuować...")

def check_system_info():
    """Wyświetla informacje o środowisku systemowym"""
    print_header("INFORMACJE O ŚRODOWISKU")
    
    # Informacje o Pythonie
    print(f"Python: {sys.version.split()[0]}")
    print(f"Interpreter: {sys.executable}")
    
    # Informacje o systemie
    import platform
    print(f"System: {platform.system()} {platform.release()}")
    print(f"Wersja: {platform.version()}")
    print(f"Architektura: {platform.architecture()[0]}")
    
    # Informacje o bazie danych
    try:
        db = next(get_db())
        db_version = db.execute(text("SELECT sqlite_version()")).scalar()
        print(f"Baza danych SQLite: {db_version}")
        db.close()
    except Exception as e:
        print(f"Baza danych: ❌ Błąd: {e}")
    
    # Zużycie pamięci
    import psutil
    try:
        memory = psutil.virtual_memory()
        print(f"\nPamięć całkowita: {memory.total // (1024*1024)} MB")
        print(f"Pamięć używana: {memory.used // (1024*1024)} MB ({memory.percent}%)")
        print(f"Pamięć wolna: {memory.available // (1024*1024)} MB")
    except:
        print("\nNie można uzyskać informacji o pamięci")
    
    # Procesy
    try:
        current_process = psutil.Process()
        print(f"\nPID procesu: {current_process.pid}")
        print(f"Użycie CPU: {current_process.cpu_percent()}%")
        print(f"Użycie pamięci: {current_process.memory_info().rss // (1024*1024)} MB")
    except:
        print("\nNie można uzyskać informacji o procesie")
    
    input("\nNaciśnij Enter, aby kontynuować...")

def run_connection_test():
    """Uruchamia diagnostykę połączenia API"""
    print_header("DIAGNOSTYKA POŁĄCZENIA API")
    
    try:
        # Sprawdź czy skrypt diagnostyczny istnieje
        if not os.path.exists("test_api_connection.py"):
            print("❌ Skrypt diagnostyczny test_api_connection.py nie istnieje!")
            input("\nNaciśnij Enter, aby kontynuować...")
            return
        
        # Uruchom skrypt diagnostyczny
        print("Uruchamianie diagnostyki połączenia...")
        subprocess.run([sys.executable, "test_api_connection.py"], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Błąd podczas uruchamiania diagnostyki: {e}")
    except Exception as e:
        print(f"❌ Wystąpił nieoczekiwany błąd: {e}")
    
    input("\nNaciśnij Enter, aby kontynuować...")

def repair_active_sessions():
    """Uruchamia skrypt naprawy aktywnych sesji"""
    print_header("NAPRAWA AKTYWNYCH SESJI")
    
    try:
        # Sprawdź czy skrypt naprawczy istnieje
        if not os.path.exists("fix_active_sessions.py"):
            print("❌ Skrypt naprawczy fix_active_sessions.py nie istnieje!")
            input("\nNaciśnij Enter, aby kontynuować...")
            return
        
        # Uruchom skrypt naprawczy
        print("Uruchamianie skryptu naprawy aktywnych sesji...")
        subprocess.run([sys.executable, "fix_active_sessions.py"], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Błąd podczas uruchamiania skryptu naprawczego: {e}")
    except Exception as e:
        print(f"❌ Wystąpił nieoczekiwany błąd: {e}")
    
    input("\nNaciśnij Enter, aby kontynuować...")

def check_database_integrity():
    """Sprawdza integralność bazy danych"""
    print_header("SPRAWDZANIE INTEGRALNOŚCI BAZY DANYCH")
    
    try:
        db = next(get_db())
        
        # Sprawdź integralność bazy danych SQLite
        integrity_check = db.execute(text("PRAGMA integrity_check")).fetchone()[0]
        
        if integrity_check == "ok":
            print("✅ Integralność bazy danych jest OK")
        else:
            print(f"❌ Problemy z integralnością bazy danych: {integrity_check}")
        
        # Sprawdź integralność tabel
        tables = [
            "employees", "shifts", "admin_logs", "users", "pin_access_logs"
        ]
        
        print("\nSprawdzanie tabel:")
        for table in tables:
            try:
                # Sprawdź istnienie tabeli
                table_exists = db.execute(text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")).fetchone()
                
                if table_exists:
                    # Podstawowe sprawdzenie poprawności tabeli
                    count = db.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                    print(f"{table:20} ✅ Istnieje ({count} rekordów)")
                else:
                    print(f"{table:20} ❌ Tabela nie istnieje!")
                    
            except Exception as e:
                print(f"{table:20} ❌ Błąd: {str(e)[:50]}")
        
    except Exception as e:
        print(f"\n❌ Błąd podczas sprawdzania integralności bazy danych: {e}")
    finally:
        db.close()
    
    input("\nNaciśnij Enter, aby kontynuować...")

def restart_api_servers():
    """Restartuje serwery API"""
    print_header("RESTART SERWERÓW API")
    
    confirm = input("\n⚠️ Czy na pewno chcesz zrestartować wszystkie serwery API? (tak/nie): ")
    if confirm.lower() != "tak":
        print("Anulowano operację.")
        return
    
    try:
        # Sprawdź czy skrypt uruchamiający serwery istnieje
        if not os.path.exists("start_api_servers.py"):
            print("❌ Skrypt start_api_servers.py nie istnieje!")
            input("\nNaciśnij Enter, aby kontynuować...")
            return
        
        # Najpierw zabij istniejące procesy
        print("Zatrzymywanie uruchomionych serwerów...")
        
        # Znajdź i zakończ procesy serwera API
        import psutil
        
        killed = 0
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.cmdline()
                if len(cmdline) > 1 and ('python' in cmdline[0].lower() or 'pythonw' in cmdline[0].lower()):
                    if ('main.py' in cmdline or 'server_alt_port.py' in cmdline or 
                        ('uvicorn' in cmdline and 'main:app' in ' '.join(cmdline))):
                        proc.terminate()
                        killed += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        if killed > 0:
            print(f"Zatrzymano {killed} procesów serwerów API.")
            # Daj czas na zakończenie procesów
            import time
            time.sleep(2)
        else:
            print("Nie znaleziono uruchomionych serwerów API.")
        
        # Uruchom serwery API
        print("\nUruchamianie serwerów API...")
        
        # Uruchom w tle, aby terminal pozostał dostępny
        subprocess.Popen([sys.executable, "start_api_servers.py"])
        
        print("✅ Serwery API zostały uruchomione pomyślnie.")
        print("Pamiętaj, że uruchomienie może potrwać kilka sekund.")
        
    except Exception as e:
        print(f"❌ Wystąpił błąd podczas restartowania serwerów: {e}")
    
    input("\nNaciśnij Enter, aby kontynuować...")

def search_employee():
    """Wyszukuje pracownika i wyświetla jego status"""
    print_header("WYSZUKIWANIE PRACOWNIKA")
    
    search_term = input("Podaj ID, nazwisko lub imię pracownika: ")
    
    if not search_term:
        print("Anulowano wyszukiwanie.")
        return
    
    try:
        db = next(get_db())
        
        # Wyszukaj pracownika
        employees = db.execute(text("""
            SELECT id, name, pin
            FROM employees
            WHERE id LIKE :search OR name LIKE :search_name
            ORDER BY name
            LIMIT 10
        """), {"search": f"%{search_term}%", "search_name": f"%{search_term}%"}).fetchall()
        
        if not employees:
            print(f"Nie znaleziono pracowników pasujących do '{search_term}'.")
            return
        
        # Wyświetl znalezionych pracowników
        print(f"\nZnaleziono {len(employees)} pracowników:")
        print(f"{'ID':6} {'Imię i nazwisko':30} {'PIN':6} {'Status':10}")
        print("-" * 60)
        
        for employee in employees:
            # Sprawdź czy pracownik ma aktywną sesję
            active_session = db.execute(text("""
                SELECT id, start_time 
                FROM shifts 
                WHERE employee_id = :employee_id AND stop_time IS NULL
            """), {"employee_id": employee[0]}).fetchone()
            
            status = "🟢 Aktywny" if active_session else "🔴 Nieaktywny"
            
            print(f"{employee[0]:6} {employee[1]:30} {employee[2] or 'brak':6} {status:10}")
            
            if active_session:
                start_time = active_session[1]
                duration = dt.datetime.now() - start_time
                hours = int(duration.total_seconds() // 3600)
                minutes = int((duration.total_seconds() % 3600) // 60)
                
                print(f"      Rozpoczęcie: {start_time.strftime('%Y-%m-%d %H:%M')}, Czas pracy: {hours}h {minutes}min")
                print(f"      ID sesji: {active_session[0]}")
        
        # Opcja zakończenia sesji dla znalezionego pracownika
        if len(employees) == 1 and active_session:
            action = input("\nCzy chcesz zakończyć sesję tego pracownika? (tak/nie): ")
            
            if action.lower() == "tak":
                # Zakończ sesję
                now = dt.datetime.now()
                db.execute(text("""
                    UPDATE shifts
                    SET stop_time = :now,
                        stop_location = 'Zakończono przez terminal diagnostyczny',
                        duration_min = CAST((julianday(:now) - julianday(start_time)) * 24 * 60 AS INTEGER)
                    WHERE id = :session_id AND stop_time IS NULL
                """), {"now": now, "session_id": active_session[0]})
                
                # Dodaj log administratora
                db.execute(text("""
                    INSERT INTO admin_logs (action_type, admin_id, target_id, action_time, notes)
                    VALUES ('FORCE_STOP', 'admin_terminal', :target_id, :action_time, 'Zakończono przez terminal diagnostyczny')
                """), {
                    "target_id": str(employees[0][0]),
                    "action_time": now
                })
                
                db.commit()
                print(f"\n✅ Pomyślnie zakończono sesję pracownika: {employees[0][1]} (ID: {employees[0][0]})")
    
    except Exception as e:
        print(f"\n❌ Błąd podczas wyszukiwania pracownika: {e}")
    finally:
        db.close()
    
    input("\nNaciśnij Enter, aby kontynuować...")

def main():
    """Główna funkcja programu"""
    try:
        # Sprawdź czy wymagane pakiety są zainstalowane
        missing_packages = []
        try:
            import requests
        except ImportError:
            missing_packages.append("requests")
        
        try:
            import psutil
        except ImportError:
            missing_packages.append("psutil")
        
        # Jeśli brakuje pakietów, próbujemy je zainstalować
        if missing_packages:
            print("Instalowanie wymaganych pakietów...")
            for package in missing_packages:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print("Pakiety zostały zainstalowane.")
        
        while True:
            option = show_menu()
            
            if option == "1":  # Zarządzanie sesjami
                while True:
                    session_option = sessions_menu()
                    
                    if session_option == "1":
                        list_active_sessions()
                    elif session_option == "2":
                        end_session()
                    elif session_option == "3":
                        end_session(all_sessions=True)
                    elif session_option == "4":
                        break
                    else:
                        print("\nNieprawidłowa opcja.")
            
            elif option == "2":  # Informacje systemowe
                while True:
                    info_option = system_info_menu()
                    
                    if info_option == "1":
                        check_server_status()
                    elif info_option == "2":
                        check_database_tables()
                    elif info_option == "3":
                        check_system_info()
                    elif info_option == "4":
                        break
                    else:
                        print("\nNieprawidłowa opcja.")
            
            elif option == "3":  # Diagnostyka połączenia
                run_connection_test()
            
            elif option == "4":  # Narzędzia naprawcze
                while True:
                    repair_option = repair_tools_menu()
                    
                    if repair_option == "1":
                        repair_active_sessions()
                    elif repair_option == "2":
                        check_database_integrity()
                    elif repair_option == "3":
                        restart_api_servers()
                    elif repair_option == "4":
                        break
                    else:
                        print("\nNieprawidłowa opcja.")
            
            elif option == "5":  # Wyjście
                print("\nZamykanie terminala diagnostycznego...\n")
                break
            
            else:
                print("\nNieprawidłowa opcja.")
    
    except KeyboardInterrupt:
        print("\n\nPrzerwano działanie terminala diagnostycznego.")
    except Exception as e:
        print(f"\nWystąpił nieoczekiwany błąd: {e}")
        input("\nNaciśnij Enter, aby zakończyć...")

if __name__ == "__main__":
    main()
