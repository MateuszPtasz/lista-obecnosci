"""
Test uprawnień do zapisu plików konfiguracyjnych
"""
import os
import time
import datetime

def test_file_permissions():
    """Test uprawnień do zapisu plików"""
    files_to_check = [
        "config.py",
        "configs/app_config.py"
    ]
    
    print("=== Test uprawnień do plików konfiguracyjnych ===")
    print(f"Data i czas: {datetime.datetime.now()}")
    print("-" * 50)
    
    for file_path in files_to_check:
        print(f"\nSprawdzanie pliku: {file_path}")
        
        # Sprawdź czy plik istnieje
        if not os.path.exists(file_path):
            print(f"✗ Plik {file_path} nie istnieje!")
            continue
            
        # Sprawdź uprawnienia do odczytu
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                file_size = len(content)
            print(f"✓ Odczyt: OK (rozmiar pliku: {file_size} bajtów)")
        except Exception as e:
            print(f"✗ Błąd odczytu: {e}")
            continue
            
        # Sprawdź uprawnienia do zapisu
        try:
            # Zapisz oryginalny czas modyfikacji
            original_mtime = os.path.getmtime(file_path)
            
            # Utwórz kopię zapasową
            backup_path = f"{file_path}.bak"
            with open(file_path, "r", encoding="utf-8") as src:
                with open(backup_path, "w", encoding="utf-8") as dst:
                    dst.write(src.read())
            print(f"✓ Kopia zapasowa: Utworzono {backup_path}")
            
            # Dodaj znacznik czasowy
            timestamp = int(time.time())
            marker = f"\n# Test zapisu: {timestamp}\n"
            
            # Dodaj znacznik do pliku
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(marker)
            print(f"✓ Dodano znacznik do pliku")
            
            # Sprawdź czy znacznik został dodany
            with open(file_path, "r", encoding="utf-8") as f:
                updated_content = f.read()
                
            if str(timestamp) in updated_content:
                print(f"✓ Zapis: OK (znacznik odnaleziony w pliku)")
            else:
                print(f"✗ Zapis: BŁĄD (nie można odnaleźć znacznika)")
                
            # Sprawdź czy czas modyfikacji się zmienił
            new_mtime = os.path.getmtime(file_path)
            if new_mtime > original_mtime:
                print(f"✓ Czas modyfikacji: Zmieniony ({new_mtime - original_mtime:.2f} s różnicy)")
            else:
                print(f"✗ Czas modyfikacji: Nie zmienił się!")
                
            # Przywróć kopię zapasową
            os.remove(file_path)
            os.rename(backup_path, file_path)
            print(f"✓ Przywrócono oryginalny plik")
            
        except Exception as e:
            print(f"✗ Błąd zapisu: {e}")
            # Spróbuj przywrócić kopię zapasową w przypadku błędu
            try:
                if os.path.exists(backup_path):
                    os.remove(file_path)
                    os.rename(backup_path, file_path)
                    print(f"✓ Przywrócono oryginalny plik po błędzie")
            except:
                print(f"✗ Nie udało się przywrócić oryginalnego pliku!")
    
    print("\n=== Zalecenia ===")
    print("1. Upewnij się, że proces Pythona ma uprawnienia do zapisu plików.")
    print("2. Sprawdź czy antywirus nie blokuje operacji zapisu.")
    print("3. Sprawdź czy dysk ma wystarczająco miejsca.")
    print("4. Uruchom serwer z uprawnieniami administratora w razie problemów.")
    print("-" * 50)

if __name__ == "__main__":
    test_file_permissions()
