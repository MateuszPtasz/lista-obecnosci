# Instrukcja wdrożenia ujednoliconego interfejsu

## Wprowadzenie

Ten dokument przedstawia instrukcję, jak wdrożyć nowy, ujednolicony design do całej aplikacji Lista Obecności. Nowy interfejs bazuje na nowoczesnym wyglądzie panelu administracyjnego i został zaimplementowany w sposób zapewniający spójny wygląd wszystkich stron.

## Struktura plików

Stworzone zostały następujące pliki w ramach nowego, ujednoliconego interfejsu:

1. `index_unified.html` - strona główna (Pulpit)
2. `employees_unified.html` - strona zarządzania pracownikami (Zespół)
3. `mobile_config_unified.html` - strona konfiguracji aplikacji mobilnej
4. `style_unified.css` - dodatkowe style dla ujednoliconego interfejsu
5. `sidebar_unified.js` - zaktualizowany skrypt obsługi menu bocznego

## Jak wdrożyć nowy interfejs

### Krok 1: Testowanie nowego interfejsu

1. Otwórz stronę `index_unified.html` w przeglądarce, aby zobaczyć nowy wygląd Pulpitu.
2. Przetestuj nawigację do stron `employees_unified.html` i `mobile_config_unified.html`.
3. Sprawdź poprawność działania funkcji na każdej z tych stron.

### Krok 2: Zastąpienie starych plików nowymi

Po potwierdzeniu, że nowy interfejs działa poprawnie:

1. Utwórz kopię zapasową oryginalnych plików:
   ```
   copy frontend\index.html frontend\index.html.bak
   copy frontend\employees.html frontend\employees.html.bak
   copy frontend\mobile_config.html frontend\mobile_config.html.bak
   copy frontend\sidebar.js frontend\sidebar.js.bak
   ```

2. Zastąp oryginalne pliki nowymi:
   ```
   copy frontend\index_unified.html frontend\index.html
   copy frontend\employees_unified.html frontend\employees.html
   copy frontend\mobile_config_unified.html frontend\mobile_config.html
   copy frontend\sidebar_unified.js frontend\sidebar.js
   ```

3. Dodaj plik z nowymi stylami do głównego katalogu:
   ```
   copy frontend\style_unified.css frontend\style_unified.css
   ```

### Krok 3: Tworzenie kolejnych stron w ujednoliconym stylu

Aby stworzyć pozostałe strony w nowym stylu (np. attendance_day.html, attendance_summary.html):

1. Użyj plików `index_unified.html` lub `employees_unified.html` jako szablonu.
2. Zmień tytuł strony, nagłówek i zawartość.
3. Upewnij się, że odpowiedni element menu jest zaznaczony jako aktywny.
4. Zachowaj spójną strukturę dokumentu:
   - Nagłówek `.content-header` z tytułem i akcjami
   - Zawartość `.content-body` z kartami `.card`
   - Stopka `.content-footer`

### Krok 4: Aktualizacja linków

Upewnij się, że wszystkie odnośniki na stronach wskazują na właściwe pliki:

1. Uaktualnij linki w menu bocznym, aby wskazywały na pliki bez sufiksu "_unified"
2. Sprawdź wszystkie przyciski i odnośniki na stronach, aby upewnić się, że kierują do odpowiednich stron

### Krok 5: Testowanie całego systemu

1. Przetestuj wszystkie funkcje aplikacji na nowym interfejsie
2. Sprawdź responsywność (jak wygląda na różnych rozmiarach ekranu)
3. Upewnij się, że menu boczne działa poprawnie na wszystkich stronach

## Mapowanie menu

Dla lepszej przejrzystości, wprowadziliśmy następujące zmiany w nazewnictwie sekcji:

| Stara nazwa     | Nowa nazwa      | Plik                     |
|-----------------|-----------------|--------------------------|
| Pracownicy      | Zespół          | employees.html           |
| Raport - Dzień  | Obecność - Dzień| attendance_day.html      |
| Raport - Miesiąc| Obecność - Ewidencja | attendance_summary.html |
| Ustawienia      | Konfiguracja    | mobile_config.html, etc. |

## Wskazówki techniczne

- W nowym interfejsie używamy klas CSS takich jak `.card`, `.content-header`, `.content-body` dla spójnej struktury.
- Style są podzielone między główny plik `style.css` i dodatkowy `style_unified.css`.
- Skrypt `sidebar_unified.js` automatycznie podświetla aktywne pozycje menu na podstawie aktualnego URL.
- Każda strona powinna zawierać odpowiednie znaczniki meta, odniesienia do plików CSS i skryptów JS.

## Rozwiązywanie problemów

Jeśli pojawią się problemy z interfejsem:

1. Sprawdź konsole przeglądarki pod kątem błędów JavaScript
2. Upewnij się, że wszystkie pliki CSS i JS są prawidłowo załadowane
3. Zweryfikuj, czy endpointy API działają poprawnie
4. Przywróć kopie zapasowe w przypadku krytycznych problemów

---

Przygotowano przez: Dział IT
Data: Sierpień 2025
