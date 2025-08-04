#!/usr/bin/env python3
"""
Prosty skrypt do dodawania pracowników do systemu lista obecności
"""

import requests
import sys

def add_worker(worker_id, name, hourly_rate=25.0, pin=None):
    """Dodaje pracownika przez API"""
    
    data = {
        "id": worker_id,
        "name": name,
        "hourly_rate": hourly_rate
    }
    
    if pin:
        data["pin"] = pin
    
    try:
        response = requests.post("http://127.0.0.1:8000/workers", json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print(f"✅ Pomyślnie dodano pracownika {worker_id}")
        else:
            print(f"❌ Błąd podczas dodawania pracownika")
            
    except Exception as e:
        print(f"❌ Błąd połączenia: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Użycie: python add_worker.py <id> <nazwa> [stawka] [pin]")
        print("Przykład: python add_worker.py mptaszkowski 'Michał Ptaszkowski' 25.0 1111")
        sys.exit(1)
    
    worker_id = sys.argv[1]
    name = sys.argv[2]
    hourly_rate = float(sys.argv[3]) if len(sys.argv) > 3 else 25.0
    pin = sys.argv[4] if len(sys.argv) > 4 else None
    
    print(f"Dodaję pracownika: {worker_id} - {name}")
    add_worker(worker_id, name, hourly_rate, pin)
