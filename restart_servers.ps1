Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "Restart serwerów Lista Obecności" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Zatrzymywanie istniejących procesów serwera..." -ForegroundColor Yellow
Get-Process -Name python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

Write-Host ""
Write-Host "Czyszczenie plików tymczasowych..." -ForegroundColor Yellow
Remove-Item -Path "*.pyc" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "__pycache__\*.pyc" -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "Uruchamianie serwera API (port 8000)..." -ForegroundColor Yellow
Start-Process -FilePath "python" -ArgumentList "main.py --port 8000" -WindowStyle Normal

Write-Host ""
Write-Host "Uruchamianie zapasowego serwera API (port 8002)..." -ForegroundColor Yellow
Start-Process -FilePath "python" -ArgumentList "main.py --port 8002" -WindowStyle Normal

Write-Host ""
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "Serwery zostały zrestartowane!" -ForegroundColor Green
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "Serwer główny:    http://localhost:8000" -ForegroundColor White
Write-Host "Serwer zapasowy:  http://localhost:8002" -ForegroundColor White
Write-Host ""
Write-Host "Aby sprawdzić status serwerów, użyj skryptu: diagnostyka_api.bat" -ForegroundColor White
Write-Host ""

Write-Host "Naciśnij dowolny klawisz, aby kontynuować..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
