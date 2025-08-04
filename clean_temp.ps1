# Skrypt czyszczacy pliki tymczasowe
Write-Host "Usuwanie plikow tymczasowych i katalogow __pycache__..."

# Usuwanie plikow __pycache__
Get-ChildItem -Path . -Filter "__pycache__" -Recurse -Directory | ForEach-Object {
    Write-Host "Usuwanie katalogu: $_"
    Remove-Item -Path $_.FullName -Recurse -Force
}

# Usuwanie plikow .pyc
Get-ChildItem -Path . -Filter "*.pyc" -Recurse -File | ForEach-Object {
    Write-Host "Usuwanie pliku: $_"
    Remove-Item -Path $_.FullName -Force
}

Write-Host "Czyszczenie zakonczone."
