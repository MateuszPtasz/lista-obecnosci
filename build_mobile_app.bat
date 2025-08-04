@echo off
echo ======================================================
echo Budowanie aplikacji mobilnej z najnowszymi zmianami
echo ======================================================
echo.

set APP_NAME=lista-obecnosci-app-diagnostyka-%date:~-4%%date:~3,2%%date:~0,2%
echo Nazwa aplikacji: %APP_NAME%
echo.

cd mobile_app

echo Czyszczenie poprzedniej kompilacji...
call flutter clean
if %ERRORLEVEL% NEQ 0 (
    echo BŁĄD: Nie udało się wyczyścić poprzedniej kompilacji.
    goto :error
)

echo.
echo Aktualizowanie zależności...
call flutter pub get
if %ERRORLEVEL% NEQ 0 (
    echo BŁĄD: Nie udało się pobrać zależności.
    goto :error
)

echo.
echo Sprawdzanie i naprawianie plików XML...
if not exist android\app\src\main\res\layout\ (
    mkdir android\app\src\main\res\layout
)

echo ^<?xml version="1.0" encoding="utf-8"?^>^<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android" android:layout_width="match_parent" android:layout_height="match_parent"^>^<TextView android:layout_width="wrap_content" android:layout_height="wrap_content" android:layout_gravity="center" android:text="Lista obecności"/^>^</FrameLayout^> > android\app\src\main\res\layout\attendance_widget.xml

echo ^<?xml version="1.0" encoding="utf-8"?^>^<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android" android:layout_width="match_parent" android:layout_height="match_parent"^>^<LinearLayout android:layout_width="match_parent" android:layout_height="match_parent" android:orientation="vertical" android:padding="8dp"^>^<TextView android:layout_width="match_parent" android:layout_height="wrap_content" android:text="Lista obecności" android:textAlignment="center" android:textStyle="bold"/^>^</LinearLayout^>^</FrameLayout^> > android\app\src\main\res\layout\attendance_widget_layout.xml

echo Pliki XML zostały naprawione.

echo.
echo Budowanie aplikacji...
call flutter build apk --release --split-per-abi --no-shrink
if %ERRORLEVEL% NEQ 0 (
    echo BŁĄD: Kompilacja nie powiodła się.
    goto :error
)

echo.
echo Kopiowanie pliku APK do głównego katalogu...
if exist build\app\outputs\flutter-apk\app-armeabi-v7a-release.apk (
    copy build\app\outputs\flutter-apk\app-armeabi-v7a-release.apk ..\%APP_NAME%.apk
) else (
    echo BŁĄD: Nie znaleziono pliku APK.
    goto :error
)

cd ..

echo.
echo ======================================================
echo Aplikacja została zbudowana pomyślnie!
echo ======================================================
echo Plik: %APP_NAME%.apk
echo.
goto :end

:error
cd ..
echo.
echo ======================================================
echo BŁĄD podczas budowania aplikacji!
echo ======================================================
echo Sprawdź logi błędów powyżej.
echo.

:end
pause