#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Narzędzie do testowania statusu zapory sieciowej
Sprawdza czy firewall jest aktywny i wyświetla/modyfikuje reguły dla Pythona
"""

import os
import sys
import subprocess
import socket
import platform
import argparse
from datetime import datetime

def print_header(text):
    """Wyświetla nagłówek sekcji"""
    border = "=" * len(text)
    print(f"\n{border}")
    print(text)
    print(f"{border}\n")

def run_command(command, print_output=True, encoding='utf-8'):
    """Uruchamia polecenie i zwraca wynik"""
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            check=False
        )
        
        stdout = result.stdout.decode(encoding, errors='replace')
        stderr = result.stderr.decode(encoding, errors='replace')
        
        if print_output:
            if stdout:
                print(stdout)
            if stderr:
                print(f"BŁĄD: {stderr}")
                
        return {
            "success": result.returncode == 0,
            "stdout": stdout,
            "stderr": stderr,
            "code": result.returncode
        }
    except Exception as e:
        if print_output:
            print(f"Wystąpił błąd podczas wykonywania polecenia: {e}")
        return {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "code": -1
        }

def check_admin():
    """Sprawdza, czy skrypt jest uruchomiony z uprawnieniami administratora"""
    try:
        if os.name == 'nt':
            # Windows
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            # Linux/Unix
            return os.geteuid() == 0
    except:
        return False

def get_python_paths():
    """Zwraca listę ścieżek do interpreterów Pythona"""
    paths = []
    
    # Ścieżka bieżącego interpretera
    paths.append(sys.executable)
    
    # W systemie Windows szukamy w typowych lokalizacjach
    if os.name == 'nt':
        program_files = os.environ.get('ProgramFiles', 'C:\\Program Files')
        program_files_x86 = os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)')
        appdata_local = os.environ.get('LOCALAPPDATA', '')
        
        search_paths = [
            os.path.join(program_files, 'Python*'),
            os.path.join(program_files_x86, 'Python*'),
            os.path.join(appdata_local, 'Programs', 'Python', 'Python*')
        ]
        
        for search_path in search_paths:
            try:
                matches = list(filter(os.path.isdir, [f for f in os.popen(f'dir /b /ad {search_path} 2>nul').read().splitlines()]))
                
                for match in matches:
                    if match.startswith('Python'):
                        if search_path.startswith(appdata_local):
                            python_path = os.path.join(appdata_local, 'Programs', 'Python', match, 'python.exe')
                        else:
                            python_path = os.path.join(search_path.replace('Python*', match), 'python.exe')
                        
                        if os.path.exists(python_path):
                            paths.append(python_path)
            except:
                pass
    
    # Usuwamy duplikaty i zwracamy unikalne ścieżki
    return list(set(paths))

def check_firewall_status():
    """Sprawdza status zapory sieciowej"""
    print_header("STATUS ZAPORY SIECIOWEJ")
    
    if os.name == 'nt':
        # Windows
        run_command("netsh advfirewall show allprofiles")
    else:
        # Linux/Unix
        run_command("sudo ufw status verbose")
        run_command("sudo iptables -L -v")

def check_python_firewall_rules():
    """Sprawdza reguły zapory dla Pythona"""
    print_header("REGUŁY ZAPORY DLA PYTHONA")
    
    python_paths = get_python_paths()
    
    if not python_paths:
        print("Nie znaleziono żadnych instalacji Pythona.")
        return
    
    print(f"Znaleziono {len(python_paths)} instalacji Pythona:")
    for i, path in enumerate(python_paths, 1):
        print(f"{i}. {path}")
    
    if os.name == 'nt':
        # Windows
        for path in python_paths:
            print(f"\nReguły dla: {path}")
            run_command(f'netsh advfirewall firewall show rule name="Python Application" dir=in')
            run_command(f'netsh advfirewall firewall show rule name="Python Application" dir=out')
    else:
        # Linux/Unix
        for path in python_paths:
            print(f"\nReguły dla: {path}")
            run_command(f"sudo iptables -L -v | grep -i {os.path.basename(path)}")

def add_firewall_rule_for_python(python_path=None, port=None):
    """Dodaje regułę zapory dla Pythona"""
    if not check_admin():
        print("Ta operacja wymaga uprawnień administratora!")
        return False
    
    if not python_path:
        python_paths = get_python_paths()
        if not python_paths:
            print("Nie znaleziono żadnych instalacji Pythona.")
            return False
        
        python_path = python_paths[0]  # Domyślnie używamy pierwszej znalezionej instalacji
    
    print_header(f"DODAWANIE REGUŁY ZAPORY DLA PYTHONA ({python_path})")
    
    if os.name == 'nt':
        # Windows
        rule_name = "Python API Server"
        
        # Usuwamy istniejącą regułę, jeśli istnieje
        run_command(f'netsh advfirewall firewall delete rule name="{rule_name}" program="{python_path}"')
        
        # Dodajemy nową regułę dla ruchu przychodzącego
        command_in = f'netsh advfirewall firewall add rule name="{rule_name}" dir=in action=allow program="{python_path}" enable=yes profile=any description="Pozwala na przychodzące połączenia do aplikacji Python"'
        
        if port:
            command_in += f" localport={port} protocol=TCP"
            
        result_in = run_command(command_in)
        
        # Dodajemy nową regułę dla ruchu wychodzącego
        command_out = f'netsh advfirewall firewall add rule name="{rule_name}" dir=out action=allow program="{python_path}" enable=yes profile=any description="Pozwala na wychodzące połączenia z aplikacji Python"'
        
        if port:
            command_out += f" localport={port} protocol=TCP"
            
        result_out = run_command(command_out)
        
        return result_in["success"] and result_out["success"]
    else:
        # Linux/Unix
        if port:
            command = f"sudo ufw allow {port}/tcp"
            return run_command(command)["success"]
        else:
            print("Dla systemów Linux/Unix wymagane jest podanie portu.")
            return False

def check_specific_port(port):
    """Sprawdza, czy określony port jest otwarty"""
    print_header(f"SPRAWDZANIE PORTU {port}")
    
    # Sprawdzenie, czy port jest zajęty lokalnie
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('0.0.0.0', port))
        s.listen(1)
        s.close()
        print(f"Port {port} jest dostępny do nasłuchiwania.")
    except socket.error:
        print(f"Port {port} jest już zajęty lub zablokowany.")
    
    # Sprawdzenie reguł zapory dla portu
    if os.name == 'nt':
        # Windows
        run_command(f'netsh advfirewall firewall show rule name=all | findstr /i "{port}"')
    else:
        # Linux/Unix
        run_command(f"sudo iptables -L -v | grep -i {port}")

def check_active_listeners():
    """Sprawdza aktywne procesy nasłuchujące na portach"""
    print_header("AKTYWNE POŁĄCZENIA NA PORTACH")
    
    if os.name == 'nt':
        # Windows
        print("Lista wszystkich aktywnych nasłuchujących TCP połączeń:")
        run_command("netstat -ano | findstr LISTENING")
        
        print("\nLista nasłuchujących połączeń na portach 8000, 8002 i 8080:")
        run_command("netstat -ano | findstr /i \":8000 :8002 :8080\"")
    else:
        # Linux/Unix
        print("Lista wszystkich aktywnych nasłuchujących TCP połączeń:")
        run_command("ss -tuln")
        
        print("\nLista nasłuchujących połączeń na portach 8000, 8002 i 8080:")
        run_command("ss -tuln | grep -E '8000|8002|8080'")

def generate_report(filename=None):
    """Generuje pełny raport diagnostyczny zapory"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"firewall_report_{timestamp}.txt"
    
    print_header(f"GENEROWANIE RAPORTU ({filename})")
    
    with open(filename, 'w', encoding='utf-8') as f:
        # Przekierowanie stdout do pliku
        old_stdout = sys.stdout
        sys.stdout = f
        
        try:
            print(f"RAPORT DIAGNOSTYCZNY ZAPORY SIECIOWEJ")
            print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"System: {platform.system()} {platform.release()} ({platform.architecture()[0]})")
            print(f"Użytkownik: {os.getlogin()}")
            print(f"Uprawnienia administratora: {'Tak' if check_admin() else 'Nie'}")
            print(f"Python: {sys.version}")
            print("\n" + "=" * 50 + "\n")
            
            check_firewall_status()
            check_python_firewall_rules()
            check_active_listeners()
            
            for port in [8000, 8002, 8080]:
                check_specific_port(port)
        finally:
            # Przywracanie stdout
            sys.stdout = old_stdout
    
    print(f"Raport zapisany do pliku: {filename}")
    return filename

def main():
    parser = argparse.ArgumentParser(description='Narzędzie do diagnostyki zapory sieciowej')
    parser.add_argument('--check', action='store_true', help='Sprawdź status zapory sieciowej')
    parser.add_argument('--add-rule', action='store_true', help='Dodaj regułę zapory dla Pythona')
    parser.add_argument('--port', type=int, help='Port do sprawdzenia lub konfiguracji')
    parser.add_argument('--python-path', help='Ścieżka do interpretera Pythona')
    parser.add_argument('--report', action='store_true', help='Generuj pełny raport diagnostyczny')
    parser.add_argument('--output', help='Nazwa pliku raportu')
    
    args = parser.parse_args()
    
    # Jeśli nie podano argumentów, pokazujemy wszystkie informacje
    if not any(vars(args).values()):
        print("Diagnostyka zapory sieciowej dla aplikacji Lista Obecności")
        print("Uruchom z --help, aby zobaczyć dostępne opcje\n")
        
        check_firewall_status()
        check_python_firewall_rules()
        check_active_listeners()
        
        if args.port:
            check_specific_port(args.port)
        else:
            for port in [8000, 8002, 8080]:
                check_specific_port(port)
        
        return
    
    if args.check:
        check_firewall_status()
        check_python_firewall_rules()
        check_active_listeners()
    
    if args.port:
        check_specific_port(args.port)
    
    if args.add_rule:
        add_firewall_rule_for_python(args.python_path, args.port)
    
    if args.report:
        generate_report(args.output)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nPrzerwano przez użytkownika")
        sys.exit(1)
    except Exception as e:
        print(f"\nWystąpił nieoczekiwany błąd: {e}")
        sys.exit(1)
