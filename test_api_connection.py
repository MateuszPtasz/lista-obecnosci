#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test połączenia z API - narzędzie diagnostyczne
"""

import sys
import requests
import json
import datetime as dt
import socket
import time
import os

# Definicja serwerów do sprawdzenia
SERVERS = [
    "http://localhost:8000",
    "http://localhost:8002",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8002",
]

# Definicja endpointów do sprawdzenia
ENDPOINTS = [
    "/api/connection-test",
    "/api/app-version",
    "/api/mobile-config",
    "/api/workers",
]

# Kod koloru w terminalu
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text):
    """Wyświetla nagłówek"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'=' * 50}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{text.center(50)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'=' * 50}{Colors.ENDC}\n")


def print_section(text):
    """Wyświetla sekcję"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{text}{Colors.ENDC}")
    print(f"{Colors.CYAN}{'-' * 50}{Colors.ENDC}")


def format_response(data):
    """Formatuje odpowiedź do wyświetlenia"""
    if isinstance(data, dict):
        return f"{{klucze: {', '.join(data.keys())}}}"
    elif isinstance(data, list):
        return f"[{len(data)} elementów]"
    else:
        return str(data)


def test_connection(url):
    """Testuje połączenie z URL"""
    try:
        response = requests.get(url, timeout=3)
        return True, response
    except requests.exceptions.ConnectionError:
        return False, None
    except requests.exceptions.Timeout:
        return False, None
    except Exception as e:
        return False, str(e)


def check_host_availability(host):
    """Sprawdza czy host jest dostępny"""
    try:
        # Usuwanie "http://" i wszystkiego po pierwszym "/"
        if "://" in host:
            host = host.split("://")[1]
        
        if "/" in host:
            host = host.split("/")[0]
        
        # Oddzielenie portu
        if ":" in host:
            host, port_str = host.split(":")
            port = int(port_str)
        else:
            port = 80  # Domyślny port HTTP
            
        socket_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_obj.settimeout(1)
        result = socket_obj.connect_ex((host, port))
        socket_obj.close()
        
        if result == 0:
            return True, f"Port {port} jest otwarty"
        else:
            return False, f"Port {port} jest zamknięty (kod: {result})"
    except Exception as e:
        return False, f"Błąd sprawdzania hosta: {str(e)}"


def test_endpoints():
    """Testuje wszystkie endpointy na wszystkich serwerach"""
    print_header("DIAGNOSTYKA POŁĄCZENIA Z API")
    
    # Informacje o systemie
    print_section("Informacje o systemie")
    print(f"Data i czas: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"System operacyjny: {os.name} / {sys.platform}")
    print(f"Python: {sys.version}")
    
    # Sprawdzenie połączenia internetowego
    print_section("Test połączenia internetowego")
    try:
        response = requests.get("https://www.google.com", timeout=3)
        print(f"{Colors.GREEN}✓ Połączenie internetowe działa (kod: {response.status_code}){Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.RED}✗ Brak połączenia internetowego: {e}{Colors.ENDC}")
    
    # Testowanie serwerów
    for server in SERVERS:
        print_section(f"Testowanie serwera: {server}")
        
        # Sprawdź dostępność hosta
        host_available, host_message = check_host_availability(server)
        if host_available:
            print(f"{Colors.GREEN}✓ {host_message}{Colors.ENDC}")
        else:
            print(f"{Colors.RED}✗ {host_message}{Colors.ENDC}")
            print(f"{Colors.YELLOW}Pomijam testy dla tego serwera{Colors.ENDC}")
            continue
            
        # Podstawowy test połączenia
        connected, response = test_connection(server)
        
        if not connected:
            print(f"{Colors.RED}✗ Nie można połączyć się z serwerem: {response if response else 'Timeout'}{Colors.ENDC}")
            continue
            
        print(f"{Colors.GREEN}✓ Podstawowe połączenie działa (kod: {response.status_code}){Colors.ENDC}")
        
        # Testowanie endpointów
        for endpoint in ENDPOINTS:
            url = f"{server}{endpoint}"
            print(f"\nTestuję endpoint: {endpoint}")
            
            try:
                response = requests.get(url, timeout=5)
                
                if response.status_code == 200:
                    print(f"{Colors.GREEN}✓ Status: {response.status_code}{Colors.ENDC}")
                    try:
                        data = response.json()
                        print(f"Odpowiedź: {format_response(data)}")
                    except:
                        print("Odpowiedź nie jest w formacie JSON")
                else:
                    print(f"{Colors.RED}✗ Status: {response.status_code}{Colors.ENDC}")
                    print(f"Treść błędu: {response.text}")
                    try:
                        data = response.json()
                        print(f"Odpowiedź JSON błędu: {json.dumps(data, indent=2)}")
                    except:
                        print("Odpowiedź błędu nie jest w formacie JSON")
            except Exception as e:
                print(f"{Colors.RED}✗ Błąd: {str(e)}{Colors.ENDC}")
    
    print_header("ZAKOŃCZONO DIAGNOSTYKĘ")


if __name__ == "__main__":
    test_endpoints()
