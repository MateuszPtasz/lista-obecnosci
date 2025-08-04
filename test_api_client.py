#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Uproszczony klient API do testowania połączenia z serwerem
Wykonuje testy na różnych adresach i portach
"""

import requests
import socket
import json
import datetime as dt
import sys
import os
import time
from urllib.parse import urlparse

# Lista adresów do testowania
SERVER_ADDRESSES = [
    'http://192.168.1.30:8000',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://192.168.1.30:8002',
    'http://localhost:8002',
    'http://127.0.0.1:8002',
    'http://192.168.1.30:8080',
]

# Kolory dla konsoli
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def print_header(text):
    """Drukuje nagłówek sekcji"""
    border = "=" * len(text)
    print(f"\n{BLUE}{border}{RESET}")
    print(f"{BLUE}{text}{RESET}")
    print(f"{BLUE}{border}{RESET}\n")

def print_result(success, message):
    """Drukuje wynik testu"""
    prefix = f"{GREEN}✓ " if success else f"{RED}✗ "
    print(f"{prefix}{message}{RESET}")

def test_socket_connection(host, port, timeout=2):
    """Testuje podstawowe połączenie socket do serwera"""
    try:
        socket_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_obj.settimeout(timeout)
        result = socket_obj.connect_ex((host, port))
        socket_obj.close()
        
        if result == 0:
            print_result(True, f"Połączenie socket do {host}:{port} działa")
            return True
        else:
            print_result(False, f"Nie można połączyć się z {host}:{port} - kod błędu: {result}")
            return False
    except socket.error as e:
        print_result(False, f"Błąd socket przy połączeniu z {host}:{port}: {e}")
        return False

def test_http_connection(url, endpoint="/", timeout=5):
    """Testuje połączenie HTTP do serwera"""
    full_url = f"{url}{endpoint}"
    try:
        response = requests.get(full_url, timeout=timeout)
        print_result(True, f"Połączenie HTTP do {full_url} działa (status: {response.status_code})")
        return response
    except requests.exceptions.RequestException as e:
        print_result(False, f"Błąd HTTP przy połączeniu z {full_url}: {e}")
        return None

def test_api_endpoint(url, endpoint="/api/connection-test", timeout=5):
    """Testuje określony endpoint API"""
    full_url = f"{url}{endpoint}"
    try:
        response = requests.get(full_url, timeout=timeout)
        if response.status_code == 200:
            print_result(True, f"Endpoint {full_url} działa (status: {response.status_code})")
            try:
                data = response.json()
                print(f"   Odpowiedź: {json.dumps(data, indent=2, ensure_ascii=False)}")
            except:
                print(f"   Odpowiedź nie jest w formacie JSON: {response.text[:100]}...")
            return response
        else:
            print_result(False, f"Endpoint {full_url} zwrócił błąd (status: {response.status_code})")
            print(f"   Odpowiedź: {response.text[:100]}...")
            return response
    except requests.exceptions.RequestException as e:
        print_result(False, f"Nie można połączyć się z {full_url}: {e}")
        return None

def test_mobile_config_endpoint(url, timeout=5):
    """Specjalny test dla endpointu /api/mobile-config"""
    endpoint = "/api/mobile-config"
    full_url = f"{url}{endpoint}"
    try:
        response = requests.get(full_url, timeout=timeout)
        if response.status_code == 200:
            print_result(True, f"Endpoint {full_url} działa (status: {response.status_code})")
            try:
                data = response.json()
                
                # Sprawdzamy format odpowiedzi
                if "config" in data and isinstance(data["config"], dict):
                    print_result(True, "Format odpowiedzi jest zgodny z oczekiwaniami aplikacji mobilnej")
                    print(f"   Struktura: {json.dumps({k: type(v).__name__ for k, v in data.items()}, indent=2, ensure_ascii=False)}")
                else:
                    print_result(False, "Format odpowiedzi NIE jest zgodny z oczekiwaniami aplikacji mobilnej")
                    print(f"   Otrzymano: {json.dumps(data, indent=2, ensure_ascii=False)}")
                return response
            except:
                print_result(False, f"Odpowiedź nie jest w formacie JSON: {response.text[:100]}...")
                return response
        else:
            print_result(False, f"Endpoint {full_url} zwrócił błąd (status: {response.status_code})")
            print(f"   Odpowiedź: {response.text[:100]}...")
            return response
    except requests.exceptions.RequestException as e:
        print_result(False, f"Nie można połączyć się z {full_url}: {e}")
        return None

def simulate_mobile_app_behavior(url):
    """Symuluje zachowanie aplikacji mobilnej przy łączeniu z API"""
    print_header(f"SYMULACJA ZACHOWANIA APLIKACJI MOBILNEJ ({url})")
    
    # 1. Sprawdzenie połączenia
    test_api_endpoint(url, "/api/connection-test")
    
    # 2. Pobranie konfiguracji
    test_mobile_config_endpoint(url)
    
    # 3. Symulacja rozpoczęcia pracy
    try:
        employee_id = "JAN001"
        payload = {
            "employee_id": employee_id,
            "czas_start": dt.datetime.now().isoformat(),
            "lokalizacja_start": {"lat": 50.0, "lon": 20.0}
        }
        
        print(f"Wysyłam dane: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        
        response = requests.post(
            f"{url}/api/start", 
            json=payload,
            timeout=5
        )
        
        if response.status_code == 200:
            print_result(True, f"Rozpoczęcie pracy dla {employee_id} powiodło się")
            print(f"   Odpowiedź: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        else:
            print_result(False, f"Rozpoczęcie pracy dla {employee_id} nie powiodło się (status: {response.status_code})")
            print(f"   Odpowiedź: {response.text[:200]}")
    except requests.exceptions.RequestException as e:
        print_result(False, f"Błąd podczas rozpoczynania pracy: {e}")

def test_network_config():
    """Sprawdza konfigurację sieciową"""
    print_header("KONFIGURACJA SIECIOWA")
    
    # Próba uzyskania adresu IP
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"Nazwa hosta: {hostname}")
        print(f"Lokalny adres IP: {local_ip}")
    except Exception as e:
        print(f"Nie można określić lokalnego adresu IP: {e}")
    
    # Próba sprawdzenia, czy firewall może blokować połączenia
    print("\nTestowanie popularnych portów:")
    for port in [80, 443, 8000, 8002, 8080]:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(('0.0.0.0', port))
            s.listen(1)
            s.close()
            print_result(True, f"Port {port} jest dostępny do nasłuchiwania")
        except socket.error:
            print_result(False, f"Port {port} jest już zajęty lub zablokowany")

def main():
    """Główna funkcja testująca"""
    print_header("DIAGNOSTYKA POŁĄCZENIA API - ROZSZERZONY TEST")
    print(f"Data i czas: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"System operacyjny: {os.name} / {sys.platform}")
    print(f"Python: {sys.version}")
    
    test_network_config()
    
    # Testuj każdy adres serwera
    for address in SERVER_ADDRESSES:
        print_header(f"TESTOWANIE SERWERA: {address}")
        url_parts = urlparse(address)
        host = url_parts.hostname
        port = url_parts.port
        
        # Test podstawowego połączenia
        socket_ok = test_socket_connection(host, port)
        
        if socket_ok:
            # Jeśli podstawowe połączenie działa, testuj HTTP
            http_resp = test_http_connection(address)
            
            if http_resp is not None:
                # Testuj endpointy API
                test_api_endpoint(address)
                test_mobile_config_endpoint(address)
                
                # Symuluj zachowanie aplikacji
                simulate_mobile_app_behavior(address)

if __name__ == "__main__":
    main()
