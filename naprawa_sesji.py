# Skrypt do zarządzania sesją i naprawy problemów z przyciskiem sesji
import os
import sys
import datetime
import traceback
import json
import urllib.request
import socket
import sqlite3
import time

def print_colored(text, color):
    """Wyświetla kolorowy tekst w terminalu"""
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "reset": "\033[0m"
    }
    print(f"{colors.get(color, '')}{text}{colors['reset']}")

def check_database_connection():
    """Sprawdza połączenie z bazą danych"""
    print_colored("\n=== Sprawdzanie połączenia z bazą danych ===", "cyan")
    
    db_path = "database.db"
    if not os.path.exists(db_path):
        print_colored(f"BŁĄD: Baza danych {db_path} nie istnieje!", "red")
        return False
    
    print_colored(f"✓ Plik bazy danych {db_path} istnieje", "green")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print_colored("✓ Połączenie z bazą danych nawiązane", "green")
        
        # Sprawdź tabele
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print_colored(f"✓ Znaleziono {len(tables)} tabel w bazie danych", "green")
        
        # Sprawdź tabelę sesji (jeśli istnieje)
        session_table_exists = False
        for table in tables:
            if 'session' in table[0].lower():
                session_table_exists = True
                print_colored(f"✓ Znaleziono tabelę sesji: {table[0]}", "green")
                
                # Sprawdź rekordy w tabeli sesji
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                    count = cursor.fetchone()[0]
                    print_colored(f"✓ Liczba rekordów w tabeli sesji: {count}", "green")
                    
                    # Sprawdź aktywne sesje
                    current_time = int(time.time())
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table[0]} WHERE expires > ?", (current_time,))
                        active_count = cursor.fetchone()[0]
                        print_colored(f"✓ Liczba aktywnych sesji: {active_count}", "green")
                    except:
                        print_colored("⚠ Nie można sprawdzić aktywnych sesji", "yellow")
                except:
                    print_colored(f"⚠ Nie można odczytać rekordów z tabeli {table[0]}", "yellow")
        
        if not session_table_exists:
            print_colored("⚠ Nie znaleziono tabeli sesji", "yellow")
        
        conn.close()
        return True
    except Exception as e:
        print_colored(f"BŁĄD: Problem z połączeniem z bazą danych: {str(e)}", "red")
        print_colored(traceback.format_exc(), "red")
        return False

def check_api_auth_endpoint():
    """Sprawdza endpoint API dla autoryzacji"""
    print_colored("\n=== Sprawdzanie API autoryzacji ===", "cyan")
    
    endpoints = [
        "http://localhost:8000/auth/status",
        "http://localhost:8080/auth/status",
        "http://127.0.0.1:8000/auth/status",
        "http://127.0.0.1:8080/auth/status"
    ]
    
    success = False
    
    for endpoint in endpoints:
        try:
            print_colored(f"Sprawdzam endpoint: {endpoint}", "yellow")
            req = urllib.request.Request(endpoint)
            response = urllib.request.urlopen(req, timeout=2)
            
            if response.status == 200:
                print_colored(f"✓ Endpoint {endpoint} działa (status 200)", "green")
                try:
                    data = response.read().decode('utf-8')
                    auth_data = json.loads(data)
                    print_colored("✓ Zwrócono poprawne dane JSON", "green")
                    print_colored(f"Dane: {json.dumps(auth_data, indent=2)}", "cyan")
                    success = True
                except:
                    print_colored("⚠ Ostrzeżenie: Otrzymano odpowiedź, ale nie jest to prawidłowy JSON", "yellow")
            else:
                print_colored(f"⚠ Endpoint {endpoint} zwrócił status {response.status}", "yellow")
                
        except urllib.error.URLError:
            print_colored(f"⚠ Nie można połączyć się z {endpoint}", "yellow")
        except socket.timeout:
            print_colored(f"⚠ Timeout przy połączeniu z {endpoint}", "yellow")
        except Exception as e:
            print_colored(f"⚠ Błąd przy sprawdzaniu {endpoint}: {str(e)}", "yellow")
    
    if not success:
        print_colored("BŁĄD: Nie można połączyć się z żadnym endpointem API autoryzacji!", "red")
        print_colored("Sprawdź czy serwery są uruchomione (porty 8000 i 8080)", "red")
    
    return success

def test_session_button():
    """Przeprowadza test funkcjonalności przycisku sesji"""
    print_colored("\n=== Test przycisku sesji ===", "cyan")
    print_colored("Sprawdzam funkcjonalność przycisku sesji:", "yellow")
    
    print_colored("1. Próba dostępu do API sesji bez autoryzacji", "white")
    session_endpoints = [
        "http://localhost:8000/auth/session",
        "http://localhost:8080/auth/session"
    ]
    
    for endpoint in session_endpoints:
        try:
            req = urllib.request.Request(endpoint)
            response = urllib.request.urlopen(req, timeout=2)
            print_colored(f"✓ Endpoint {endpoint} dostępny bez autoryzacji (status {response.status})", "green")
        except urllib.error.HTTPError as e:
            if e.code == 401:
                print_colored(f"✓ Endpoint {endpoint} wymaga autoryzacji (401 Unauthorized) - to oczekiwane zachowanie", "green")
            else:
                print_colored(f"⚠ Endpoint {endpoint} zwrócił nieoczekiwany kod błędu: {e.code}", "yellow")
        except Exception as e:
            print_colored(f"⚠ Błąd przy sprawdzaniu {endpoint}: {str(e)}", "yellow")
    
    print_colored("\nDiagnostyka przycisku sesji:", "yellow")
    print_colored("- Problem z przyciskiem sesji może wynikać z braku autoryzacji lub błędów w obsłudze sesji", "white")
    print_colored("- Sprawdź czy jesteś zalogowany przed użyciem funkcji związanych z sesją", "white")
    print_colored("- Sprawdź logi serwera pod kątem błędów związanych z autoryzacją", "white")
    
    return True

def repair_session_problems():
    """Próbuje naprawić typowe problemy z sesją"""
    print_colored("\n=== Próba naprawy problemów z sesją ===", "cyan")
    
    print_colored("1. Czyszczenie starych sesji w bazie danych", "yellow")
    try:
        db_path = "database.db"
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Znajdź tabelę sesji
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%session%';")
            session_tables = cursor.fetchall()
            
            if session_tables:
                for table in session_tables:
                    table_name = table[0]
                    print_colored(f"Znaleziono tabelę sesji: {table_name}", "green")
                    
                    # Sprawdź czy tabela ma kolumnę 'expires'
                    try:
                        cursor.execute(f"PRAGMA table_info({table_name})")
                        columns = cursor.fetchall()
                        has_expires = any(col[1] == 'expires' for col in columns)
                        
                        if has_expires:
                            # Usuń wygasłe sesje
                            current_time = int(time.time())
                            cursor.execute(f"DELETE FROM {table_name} WHERE expires < ?", (current_time,))
                            deleted_count = cursor.rowcount
                            conn.commit()
                            print_colored(f"✓ Usunięto {deleted_count} wygasłych sesji z tabeli {table_name}", "green")
                        else:
                            print_colored(f"⚠ Tabela {table_name} nie ma kolumny 'expires'", "yellow")
                    except Exception as e:
                        print_colored(f"⚠ Błąd podczas czyszczenia tabeli {table_name}: {str(e)}", "yellow")
            else:
                print_colored("⚠ Nie znaleziono tabeli sesji w bazie danych", "yellow")
                
            conn.close()
            print_colored("✓ Zakończono czyszczenie sesji", "green")
        else:
            print_colored(f"⚠ Nie znaleziono bazy danych {db_path}", "yellow")
    except Exception as e:
        print_colored(f"BŁĄD: Problem podczas czyszczenia sesji: {str(e)}", "red")
        print_colored(traceback.format_exc(), "red")
    
    print_colored("\nZalecane kroki:", "yellow")
    print_colored("1. Zrestartuj serwery używając skryptu restart_servers.bat", "white")
    print_colored("2. Wyczyść dane sesji w przeglądarce (ciasteczka i dane lokalne)", "white")
    print_colored("3. Zaloguj się ponownie w aplikacji", "white")
    
    return True

def main():
    """Główna funkcja diagnostyczna"""
    print_colored("=============================================", "cyan")
    print_colored("      DIAGNOSTYKA I NAPRAWA SESJI TERMINAL   ", "cyan")
    print_colored("=============================================", "cyan")
    print_colored(f"Data: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "yellow")
    
    results = []
    results.append(("Baza danych", check_database_connection()))
    results.append(("API autoryzacji", check_api_auth_endpoint()))
    results.append(("Test przycisku sesji", test_session_button()))
    
    print_colored("\n=============================================", "cyan")
    print_colored("             WYNIKI DIAGNOSTYKI              ", "cyan")
    print_colored("=============================================", "cyan")
    
    for name, result in results:
        status = "✓ OK" if result else "✗ BŁĄD"
        color = "green" if result else "red"
        print_colored(f"{name}: {status}", color)
    
    # Próba naprawy problemów
    repair_session_problems()
    
    print_colored("\n=============================================", "cyan")
    print_colored("             INSTRUKCJE URUCHOMIENIA         ", "cyan")
    print_colored("=============================================", "cyan")
    print_colored("W terminalu VS Code:", "yellow")
    print_colored("  .\\diagnoza_konfiguracji.bat", "white")
    print_colored("W terminalu webowym:", "yellow")
    print_colored("  python diagnoza_web_terminal.py", "white")
    print_colored("  python naprawa_sesji.py", "white")
    print_colored("Restart serwerów:", "yellow")
    print_colored("  .\restart_servers.bat", "white")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print_colored(f"BŁĄD KRYTYCZNY: {str(e)}", "red")
        print_colored(traceback.format_exc(), "red")
        sys.exit(1)
