"""
Test endpointu konfiguracji API
"""
import json
import requests
from configs.app_config import APP_PORT_MAIN, APP_PORT_ALT, APP_DEFAULT_IP

def test_config_endpoint():
    """Test endpointu /api/app-version i /mobile-config"""
    base_urls = [
        f"http://localhost:{APP_PORT_MAIN}",
        f"http://127.0.0.1:{APP_PORT_MAIN}",
    ]
    
    endpoints = [
        "/api/app-version",
        "/mobile-config"
    ]
    
    results = []
    
    print("Testowanie endpointów konfiguracji...")
    
    for base_url in base_urls:
        print(f"\nTestowanie serwera: {base_url}")
        
        for endpoint in endpoints:
            url = f"{base_url}{endpoint}"
            print(f"- Testowanie endpointu: {url}")
            
            try:
                response = requests.get(url, timeout=2)
                print(f"  Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"  Odpowiedź: {json.dumps(data, indent=2, ensure_ascii=False)}")
                    
                    # Sprawdź czy config_version jest w odpowiedzi
                    if endpoint == "/api/app-version" and "config_version" in data:
                        print(f"  ✓ Znaleziono config_version: {data['config_version']}")
                    else:
                        print("  ✗ Brak config_version w odpowiedzi!")
                        
                    results.append({
                        "url": url,
                        "success": True,
                        "data": data
                    })
                else:
                    print(f"  ✗ Błąd: Nieprawidłowy status odpowiedzi: {response.status_code}")
                    results.append({
                        "url": url,
                        "success": False,
                        "error": f"Status code: {response.status_code}"
                    })
            except requests.exceptions.RequestException as e:
                print(f"  ✗ Błąd połączenia: {e}")
                results.append({
                    "url": url,
                    "success": False,
                    "error": str(e)
                })
    
    print("\n=== PODSUMOWANIE ===")
    successful = sum(1 for r in results if r["success"])
    print(f"Udane testy: {successful}/{len(results)}")
    
    if successful == 0:
        print("\nUWAGA: Żaden test nie zakończył się sukcesem!")
        print("Sprawdź czy serwer jest uruchomiony i dostępny.")
        print("Możesz uruchomić serwer ręcznie komendą:")
        print(f"python -m uvicorn main:app --host 0.0.0.0 --port {APP_PORT_MAIN}")
    
    # Sprawdź czy /mobile-config działa
    mobile_config_tests = [r for r in results if "/mobile-config" in r["url"] and r["success"]]
    if not mobile_config_tests:
        print("\nUWAGA: Endpoint /mobile-config nie działa!")
        print("Sprawdź czy endpoint został poprawnie zaimplementowany w main.py.")
    
    return results

if __name__ == "__main__":
    test_config_endpoint()
