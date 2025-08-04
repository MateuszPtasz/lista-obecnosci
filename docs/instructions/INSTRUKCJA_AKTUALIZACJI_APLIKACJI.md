# 🚀 INSTRUKCJA PROCESU AKTUALIZACJI APLIKACJI
Data: 28 lipca 2025

## 📱 KOMPLETNY WORKFLOW AKTUALIZACJI

### ETAP 1: Przygotowanie nowej wersji aplikacji

#### 1.1 Modyfikacja kodu aplikacji Flutter
```bash
cd m:\Programowanie\lista_obecnosci\mobile_app
# Wprowadź zmiany w kodzie aplikacji
```

#### 1.2 Aktualizacja wersji w pubspec.yaml
```yaml
# Zmień w pliku mobile_app/pubspec.yaml
version: 1.1.0+2  # Z 1.0.0+1 na 1.1.0+2
```

#### 1.3 Budowanie APK dla Google Play
```bash
flutter build appbundle --release
# lub dla testów:
flutter build apk --release
```

---

### ETAP 2: Publikacja w Google Play Store

#### 2.1 Konto Google Play Developer
- **Koszt**: $25 jednorazowo (lifetime)
- **Link**: https://play.google.com/console
- **Proces**: Rejestracja → Płatność → Weryfikacja (2-3 dni)

#### 2.2 Upload do Google Play Console
1. Zaloguj się do Google Play Console
2. Wybierz swoją aplikację (lub utwórz nową)
3. Przejdź do "Production" → "Create new release"
4. Upload pliku `.aab` z `build/app/outputs/bundle/release/`
5. Wypełnij "Release notes" (co nowego)
6. Kliknij "Review release" → "Start rollout to production"

#### 2.3 Proces publikacji
- **Czas weryfikacji**: 1-3 dni (pierwsza publikacja może trwać tydzień)
- **Status**: Draft → In review → Pending publication → Live
- **Link do aplikacji**: Otrzymasz po publikacji (format: `https://play.google.com/store/apps/details?id=com.yourpackage.name`)

---

### ETAP 3: Konfiguracja serwera

#### 3.1 Aktualizacja APP_VERSION_INFO w config.py
```python
APP_VERSION_INFO = {
    "current_version": "1.1.0",  # NOWA WERSJA
    "minimum_version": "1.0.0",  # Minimalna obsługiwana
    "update_required": False,    # True = wymuszenie aktualizacji
    "update_message": "Nowa wersja z ulepszeniami!",
    "play_store_url": "https://play.google.com/store/apps/details?id=TWOJ_PRAWDZIWY_PACKAGE_ID",
    "update_features": [
        "Nowe funkcje które dodałeś",
        "Poprawki błędów", 
        "Ulepszenia wydajności"
    ]
}
```

#### 3.2 Opcje wymuszenia aktualizacji:

**Opcja A: Aktualizacja opcjonalna**
```python
"current_version": "1.1.0",
"minimum_version": "1.0.0",  # Stara wersja nadal działa
"update_required": False
```

**Opcja B: Aktualizacja wymagana**
```python
"current_version": "1.1.0", 
"minimum_version": "1.1.0",  # Stara wersja przestaje działać
"update_required": True
```

---

### ETAP 4: Interfejs webowy do zarządzania

#### 4.1 Zakładka "Konfiguracja Aplikacji"
Już masz w systemie! W menu głównym:
- Konfiguracja → Konfiguracja Aplikacji
- Tam możesz edytować wszystkie ustawienia

#### 4.2 Potrzebne pola w interfejsie:
- ✅ **Aktualna wersja** (input)
- ✅ **Minimalna wersja** (input)  
- ✅ **Link do Play Store** (input)
- ✅ **Wiadomość o aktualizacji** (textarea)
- ✅ **Lista nowych funkcji** (dynamic list)
- ⚠️ **Przycisk "Wymusz aktualizację"** (checkbox)

---

### ETAP 5: Praktyczny scenariusz

#### Scenariusz: Aktualizacja z wersji 1.0.0 na 1.1.0

**KROK 1: Nowa aplikacja gotowa**
```bash
# W mobile_app/pubspec.yaml
version: 1.1.0+2

# Zbuduj i upload do Google Play
flutter build appbundle --release
```

**KROK 2: Aplikacja w Google Play Store**
- Status: "Live" w Google Play Console
- Link: `https://play.google.com/store/apps/details?id=com.twoja.lista_obecnosci`

**KROK 3: Aktualizacja serwera**
```python
# config.py
APP_VERSION_INFO = {
    "current_version": "1.1.0",
    "minimum_version": "1.0.0",  # Stara jeszcze działa
    "update_required": False,    # Opcjonalna na początku
    "play_store_url": "https://play.google.com/store/apps/details?id=com.twoja.lista_obecnosci"
}
```

**KROK 4: Po kilku dniach - wymuszenie aktualizacji**
```python
# Jeśli chcesz wymusić aktualizację starych wersji
APP_VERSION_INFO = {
    "current_version": "1.1.0", 
    "minimum_version": "1.1.0",  # Teraz wymagana!
    "update_required": True
}
```

---

### ETAP 6: Co dzieje się w aplikacji mobilnej

#### 6.1 Sprawdzanie wersji przy starcie
```dart
// Aplikacja wysyła żądanie do serwera
POST http://twoj-serwer.com/app-version/check
{
  "current_version": "1.0.0"  // Wersja z pubspec.yaml
}
```

#### 6.2 Odpowiedź serwera
```json
{
  "update_available": true,
  "update_required": false,
  "update_message": "Nowa wersja z ulepszeniami!",
  "play_store_url": "https://play.google.com/store/apps/details?id=...",
  "features": ["Nowe funkcje", "Poprawki"]
}
```

#### 6.3 Reakcja aplikacji
- **update_required = false**: Dialog "Aktualizacja dostępna" z opcją "Później"
- **update_required = true**: Dialog blokujący "Wymagana aktualizacja" bez opcji pominięcia

---

### ETAP 7: Zarządzanie przez panel webowy

#### 7.1 Tworzenie interfejsu zarządzania
Potrzebujesz stronę w panelu admin:
- `frontend/app_version_management.html`
- Formularz do edycji APP_VERSION_INFO
- Przycisk "Zastosuj zmiany"
- Podgląd aktualnych ustawień

#### 7.2 Endpoint aktualizacji (już masz!)
```python
# main.py - już istnieje!
@app.post("/mobile-config")
async def update_mobile_config(config_data: dict = Body(...)):
    # Aktualizuje config.py automatycznie
```

---

## 🎯 PODSUMOWANIE PROCESU

1. **Deweloper** → Nowa wersja aplikacji → Build APK/AAB
2. **Google Play** → Upload → Weryfikacja → Publikacja (1-3 dni)
3. **Panel Admin** → Aktualizacja config.py → Ustawienie linku Play Store
4. **Użytkownicy** → Otwierają aplikację → Widzą powiadomienie o aktualizacji
5. **Opcjonalnie** → Panel Admin → Wymuszenie aktualizacji po czasie

## 💡 WSKAZÓWKI

- **Testuj najpierw** z `update_required: false`
- **Poczekaj kilka dni** przed wymuszeniem aktualizacji
- **Sprawdź logi** czy użytkownicy aktualizują
- **Miej plan wycofania** w razie problemów

---
**Chcesz żebym stworzył interfejs zarządzania wersjami w panelu admin?** 🚀
