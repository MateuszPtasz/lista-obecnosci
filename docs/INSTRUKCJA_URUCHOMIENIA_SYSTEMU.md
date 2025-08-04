# INSTRUKCJA RĘCZNEGO URUCHOMIENIA SYSTEMU LISTA OBECNOŚCI

## 1. Uruchomienie serwerów API

### Przygotowanie środowiska wirtualnego (jeśli nie istnieje)

1. Otwórz terminal i przejdź do katalogu projektu:
   ```powershell
   cd m:\Programowanie\lista_obecnosci
   ```

2. Utwórz nowe środowisko wirtualne (tylko jeśli nie istnieje):
   ```powershell
   python -m venv venv
   ```

3. Aktywuj środowisko wirtualne:
   ```powershell
   .\venv_new\Scripts\activate
   ```

   **Ważne**: Po aktywacji powinieneś zobaczyć `(venv_new)` przed promptem.

4. Zainstaluj wymagane pakiety:
   ```powershell
   .\venv_new\Scripts\pip.exe install fastapi uvicorn sqlalchemy httpx
   ```
   
   **Uwaga**: Używamy bezwzględnych ścieżek do `pip.exe` i `python.exe` z powodu problemów ze ścieżkami w niektórych konfiguracjach.

### Uruchomienie serwerów API (rekomendowana metoda)

1. Użyj przygotowanego skryptu, który uruchomi oba serwery:
   ```powershell
   .\start_servers_new.bat
   ```
   
   Alternatywnie, możesz użyć polecenia:
   ```powershell
   .\venv_new\Scripts\python.exe start_api_servers.py
   ```
   
   Ten skrypt automatycznie uruchomi główny serwer na porcie 8000 i zapasowy na porcie 8002.

### Uruchomienie głównego serwera API (port 8000) - metoda manualna

1. W aktywowanym środowisku wirtualnym wykonaj:
   ```powershell
   .\venv_new\Scripts\uvicorn.exe main:app --host 0.0.0.0 --port 8000
   ```

### Uruchomienie zapasowego serwera API (port 8002) - metoda manualna

1. Otwórz nowy terminal i powtórz kroki aktywacji środowiska wirtualnego.

2. Uruchom drugi serwer na porcie 8002:
   ```powershell
   .\venv_new\Scripts\uvicorn.exe main:app --host 0.0.0.0 --port 8002
   ```

## 2. Budowanie aplikacji mobilnej

### Przygotowanie środowiska Flutter

1. Otwórz nowy terminal i przejdź do katalogu aplikacji mobilnej:
   ```powershell
   cd m:\Programowanie\lista_obecnosci\mobile_app
   ```

2. Sprawdź, czy Flutter jest zainstalowany i dostępny:
   ```powershell
   flutter --version
   ```

3. Pobierz zależności projektu:
   ```powershell
   flutter pub get
   ```

### Naprawa brakujących plików XML (jeśli wystąpiły błędy)

Jeśli podczas budowania aplikacji wystąpiły błędy związane z plikami XML, utwórz brakujące pliki:

1. Sprawdź, czy istnieje katalog dla plików układu:
   ```powershell
   mkdir android\app\src\main\res\layout -Force
   ```

2. Utwórz plik `attendance_widget.xml`:
   ```powershell
   @"
<?xml version="1.0" encoding="utf-8"?>
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android" 
    android:layout_width="match_parent" 
    android:layout_height="match_parent">
    <TextView 
        android:layout_width="wrap_content" 
        android:layout_height="wrap_content" 
        android:layout_gravity="center" 
        android:text="Lista obecności"/>
</FrameLayout>
"@ | Out-File -FilePath android\app\src\main\res\layout\attendance_widget.xml -Encoding utf8
   ```

3. Utwórz plik `attendance_widget_layout.xml`:
   ```powershell
   @"
<?xml version="1.0" encoding="utf-8"?>
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android" 
    android:layout_width="match_parent" 
    android:layout_height="match_parent">
    <LinearLayout 
        android:layout_width="match_parent" 
        android:layout_height="match_parent" 
        android:orientation="vertical" 
        android:padding="8dp">
        <TextView 
            android:layout_width="match_parent" 
            android:layout_height="wrap_content" 
            android:text="Lista obecności" 
            android:textAlignment="center" 
            android:textStyle="bold"/>
    </LinearLayout>
</FrameLayout>
"@ | Out-File -FilePath android\app\src\main\res\layout\attendance_widget_layout.xml -Encoding utf8
   ```

### Budowanie aplikacji

1. Wyczyść poprzednie kompilacje (opcjonalnie):
   ```powershell
   flutter clean
   ```

2. Zbuduj aplikację w trybie debug:
   ```powershell
   flutter build apk --debug
   ```

   **Alternatywnie** w trybie release (dla lepszej wydajności):
   ```powershell
   flutter build apk --release
   ```

3. Skopiuj plik APK do głównego katalogu projektu:
   ```powershell
   copy build\app\outputs\flutter-apk\app-debug.apk ..\lista-obecnosci-app-debug.apk
   ```

## 3. Diagnostyka połączenia

### Uruchomienie diagnostyki API

1. Aktywuj środowisko wirtualne (jeśli jeszcze nie jest aktywne):
   ```powershell
   cd m:\Programowanie\lista_obecnosci
   .\venv\Scripts\activate
   ```

2. Zainstaluj wymagane pakiety do diagnostyki:
   ```powershell
   .\venv\Scripts\pip.exe install requests
   ```

3. Uruchom skrypt diagnostyczny:
   ```powershell
   .\venv_new\Scripts\python.exe test_api_connection.py
   ```

## 4. Rozwiązywanie problemów

### Naprawa problemów z aktywnymi sesjami pracowników

Jeśli w panelu administratora widoczni są pracownicy jako aktywni, ale próba zakończenia ich pracy kończy się błędem 400 Bad Request, można użyć dedykowanego skryptu naprawczego:

1. Aktywuj środowisko wirtualne:
   ```powershell
   .\venv_new\Scripts\activate
   ```

2. Uruchom skrypt naprawczy:
   ```powershell
   python fix_active_sessions.py
   ```

3. W menu skryptu możesz wybrać jedną z opcji:
   - **Zakończ jedną zmianę** - wybierz konkretną zmianę do zakończenia
   - **Zakończ wszystkie zmiany** - zakończ wszystkie aktywne zmiany jednocześnie
   - **Wyjdź** - wyjście ze skryptu bez dokonywania zmian

4. Po zakończeniu sprawdź, czy wszystkie problematyczne sesje zostały zamknięte:
   ```powershell
   python check_active_shifts.py
   ```

Gdy zakończysz naprawianie aktywnych sesji, zrestartuj serwery API, aby upewnić się, że zmiany zostały w pełni zastosowane:
```powershell
python start_api_servers.py
```

### Problem: "System nie może odnaleźć określonej ścieżki"

Ten błąd występuje, gdy PowerShell próbuje użyć globalnej ścieżki do Python zamiast wersji w środowisku wirtualnym.

**Rozwiązanie**:
1. Użyj pełnej ścieżki do interpretera Python w środowisku wirtualnym:
   ```powershell
   .\venv_new\Scripts\python.exe main.py --port 8000
   ```

2. Jeśli to nie pomaga, sprawdź czy środowisko wirtualne jest poprawnie utworzone:
   ```powershell
   python -m venv venv --clear
   ```

### Problem: "ModuleNotFoundError: No module named 'fastapi'"

**Rozwiązanie**:
1. Upewnij się, że używasz Pythona ze środowiska wirtualnego:
   ```powershell
   .\venv_new\Scripts\pip.exe install fastapi uvicorn sqlalchemy
   ```

### Problem: "Address already in use"

**Rozwiązanie**:
1. Sprawdź, czy porty 8000/8002 nie są już używane:
   ```powershell
   netstat -ano | findstr :8000
   ```

2. Zakończ proces używający portu (gdzie XXXX to numer procesu):
   ```powershell
   taskkill /F /PID XXXX
   ```

3. Alternatywnie użyj innego portu:
   ```powershell
   .\venv_new\Scripts\python.exe main.py --port 8888
   ```

### Uruchamianie serwerów bezpośrednio w terminalu VS Code

Jeśli chcesz uruchomić serwery bezpośrednio w terminalu VS Code (aby widzieć logi):

1. Otwórz terminal w VS Code (Ctrl+` lub "Terminal" -> "New Terminal")
2. Aktywuj środowisko wirtualne:
   ```powershell
   .\venv_new\Scripts\activate
   ```
3. Uruchom główny serwer API:
   ```powershell
   python start_api_servers.py
   ```
   
   Lub alternatywnie uruchom serwery indywidualnie:
   ```powershell
   python main.py --port 8000
   ```

### Problem: "Błąd podczas zapisywania konfiguracji: Method Not Allowed"

**Rozwiązanie**:
1. Sprawdź, czy endpoint `/api/mobile-config` obsługuje metodę POST w pliku `main.py`
2. Sprawdź, czy w pliku `api.dart` funkcja `buildApiUrl` jest używana do wszystkich zapytań
3. Uruchom diagnostykę API, aby sprawdzić wszystkie endpointy:
   ```powershell
   .\venv_new\Scripts\python.exe test_api_connection.py
   ```

## 5. Konfiguracja portów i adresów IP

W aplikacji mobilnej adres serwera API jest skonfigurowany w pliku:
`mobile_app\lib\api.dart`

Domyślnie aplikacja próbuje połączyć się z kilkoma adresami w następującej kolejności:
1. `http://192.168.1.35:8000` (główny serwer API w sieci lokalnej)
2. `http://localhost:8000` (lokalny host na porcie 8000)
3. `http://127.0.0.1:8000` (adres pętli zwrotnej na porcie 8000)
4. `http://192.168.1.35:8002` (zapasowy serwer API w sieci lokalnej)
5. `http://localhost:8002` (lokalny host na porcie 8002)
6. `http://192.168.1.35:8080` (alternatywny port 8080)

Jeśli konieczna jest zmiana adresu IP, należy edytować listę `_serverAddresses` w pliku `api.dart`.
