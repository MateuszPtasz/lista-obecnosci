# Skrypt diagnostyczny sieci dla aplikacji lista obecności
# Testuje połączenia sieciowe i konfigurację portów
# Uruchamiany z PowerShell

# Wyświetla nagłówek sekcji z kolorami
function Write-Header {
    param (
        [string] $Text
    )
    
    $border = "=" * $Text.Length
    Write-Host "`n$border" -ForegroundColor Cyan
    Write-Host $Text -ForegroundColor Cyan
    Write-Host "$border`n" -ForegroundColor Cyan
}

# Wyświetla wynik testu z kolorowym znacznikiem
function Write-Result {
    param (
        [bool] $Success,
        [string] $Message
    )
    
    $prefix = if ($Success) { "[+] " } else { "[-] " }
    $color = if ($Success) { "Green" } else { "Red" }
    
    Write-Host "$prefix$Message" -ForegroundColor $color
}

# Sprawdza czy port jest otwarty na określonym adresie
function Test-Port {
    param (
        [string] $ComputerName,
        [int] $Port,
        [int] $Timeout = 1000
    )
    
    try {
        $tcpClient = New-Object System.Net.Sockets.TcpClient
        $connect = $tcpClient.BeginConnect($ComputerName, $Port, $null, $null)
        $wait = $connect.AsyncWaitHandle.WaitOne($Timeout, $false)
        
        if ($wait) {
            try {
                $tcpClient.EndConnect($connect)
                return $true
            } catch {
                return $false
            }
        } else {
            return $false
        }
    } catch {
        return $false
    } finally {
        if ($tcpClient) {
            $tcpClient.Close()
        }
    }
}

# Pobiera informacje o systemie
function Get-SystemInfo {
    Write-Header "INFORMACJE O SYSTEMIE"
    
    $computerInfo = Get-CimInstance Win32_ComputerSystem
    $osInfo = Get-CimInstance Win32_OperatingSystem
    
    Write-Host "Nazwa komputera: $($env:COMPUTERNAME)"
    Write-Host "Użytkownik: $($env:USERNAME)"
    Write-Host "System operacyjny: $($osInfo.Caption) $($osInfo.Version)"
    Write-Host "Producent: $($computerInfo.Manufacturer)"
    Write-Host "Model: $($computerInfo.Model)"
    
    # Sprawdzanie czy PowerShell działa z uprawnieniami administratora
    $currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    $isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    
    Write-Host "Uprawnienia administratora: $($isAdmin)" -ForegroundColor $(if ($isAdmin) { "Green" } else { "Yellow" })
    
    if (-not $isAdmin) {
        Write-Host "UWAGA: Niektóre testy mogą nie działać bez uprawnień administratora" -ForegroundColor Yellow
    }
}

# Testuje połączenie sieciowe
function Test-NetworkConfiguration {
    Write-Header "KONFIGURACJA SIECIOWA"
    
    # Pobieranie informacji o interfejsach sieciowych
    $networkInterfaces = Get-NetAdapter | Where-Object { $_.Status -eq "Up" }
    
    if ($networkInterfaces.Count -eq 0) {
        Write-Result -Success $false -Message "Nie znaleziono aktywnych interfejsów sieciowych"
        return
    }
    
    Write-Host "Aktywne interfejsy sieciowe:"
    foreach ($interface in $networkInterfaces) {
        $ipConfig = Get-NetIPAddress -InterfaceIndex $interface.ifIndex -AddressFamily IPv4
        Write-Host "  - $($interface.Name): $($ipConfig.IPAddress) (Status: $($interface.Status))"
    }
    
    # Pobieranie lokalnego adresu IP
    $localIPs = @(Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -ne "127.0.0.1" })
    Write-Host "`nLokalne adresy IP:"
    foreach ($ip in $localIPs) {
        Write-Host "  - $($ip.IPAddress) (Interfejs: $($ip.InterfaceAlias))"
    }
}

# Testuje usługi związane z Windows Firewall
function Test-FirewallServices {
    Write-Header "USŁUGI WINDOWS FIREWALL"
    
    $firewallService = Get-Service -Name "MpsSvc" -ErrorAction SilentlyContinue
    
    if ($firewallService) {
        Write-Result -Success ($firewallService.Status -eq "Running") `
                    -Message "Usługa Windows Firewall (MpsSvc): $($firewallService.Status)"
    } else {
        Write-Result -Success $false -Message "Nie można znaleźć usługi Windows Firewall"
    }
    
    # Sprawdzanie ustawień zapory
    try {
        $firewallProfiles = Get-NetFirewallProfile -ErrorAction Stop
        
        Write-Host "`nProfile zapory Windows:"
        foreach ($profile in $firewallProfiles) {
            $status = if ($profile.Enabled) { "Włączony" } else { "Wyłączony" }
            $color = if ($profile.Enabled) { "Yellow" } else { "Green" }
            Write-Host "  - $($profile.Name): $status" -ForegroundColor $color
        }
    } catch {
        Write-Result -Success $false -Message "Nie można uzyskać informacji o profilach zapory: $_"
    }
    
    # Sprawdzanie reguł dla aplikacji
    $appPaths = @(
        "$env:ProgramFiles\Python*\python.exe",
        "$env:LocalAppData\Programs\Python\Python*\python.exe"
    )
    
    Write-Host "`nSprawdzanie reguł zapory dla Pythona:"
    
    $pythonFound = $false
    foreach ($path in $appPaths) {
        $pythonExes = Get-Item -Path $path -ErrorAction SilentlyContinue
        
        foreach ($pythonExe in $pythonExes) {
            $pythonFound = $true
            $rules = Get-NetFirewallApplicationFilter -Program $pythonExe.FullName -ErrorAction SilentlyContinue | 
                     Get-NetFirewallRule -ErrorAction SilentlyContinue
            
            if ($rules) {
                Write-Result -Success $true -Message "Znaleziono reguły dla $($pythonExe.FullName)"
                foreach ($rule in $rules) {
                    $status = if ($rule.Enabled) { "Włączona" } else { "Wyłączona" }
                    $direction = if ($rule.Direction -eq "Inbound") { "Przychodzące" } else { "Wychodzące" }
                    Write-Host "    - $($rule.DisplayName) ($direction): $status"
                }
            } else {
                Write-Result -Success $false -Message "Brak reguł dla $($pythonExe.FullName)"
            }
        }
    }
    
    if (-not $pythonFound) {
        Write-Result -Success $false -Message "Nie znaleziono instalacji Pythona"
    }
}

# Testuje porty używane przez aplikację
function Test-ApplicationPorts {
    param (
        [string[]] $Hosts = @("localhost", "127.0.0.1"),
        [int[]] $Ports = @(8000, 8002, 8080)
    )
    
    Write-Header "TEST PORTÓW APLIKACJI"
    
    foreach ($hostname in $Hosts) {
        Write-Host "Testowanie portów na hoście: $hostname"
        
        foreach ($port in $Ports) {
            $isOpen = Test-Port -ComputerName $hostname -Port $port
            Write-Result -Success $isOpen -Message "Port $port na $hostname: $(if ($isOpen) { 'Otwarty' } else { 'Zamknięty/Zablokowany' })"
        }
        
        Write-Host ""
    }
    
    # Sprawdzamy czy na tych portach działa jakiś proces
    Write-Host "Procesy nasłuchujące na portach:"
    foreach ($port in $Ports) {
        $netstat = netstat -ano | findstr ":$port "
        
        if ($netstat) {
            $lines = $netstat -split "`r`n"
            foreach ($line in $lines) {
                if ($line -match ":$port\s+.*LISTENING\s+(\d+)") {
                    $processId = $matches[1]
                    try {
                        $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
                        Write-Host "  - Port $port: $($process.Name) (PID: $processId, Ścieżka: $($process.Path))"
                    } catch {
                        Write-Host "  - Port $port: PID $processId (nie można określić procesu)"
                    }
                }
            }
        } else {
            Write-Host "  - Port $port: Brak procesu nasłuchującego"
        }
    }
}

# Testuje dostęp do API
function Test-ApiEndpoints {
    param (
        [string[]] $ApiUrls = @(
            "http://localhost:8000",
            "http://127.0.0.1:8000",
            "http://localhost:8002",
            "http://127.0.0.1:8002"
        ),
        [string[]] $Endpoints = @(
            "/api/connection-test",
            "/api/mobile-config"
        )
    )
    
    Write-Header "TEST ENDPOINTÓW API"
    
    foreach ($baseUrl in $ApiUrls) {
        Write-Host "Testowanie API na: $baseUrl"
        
        foreach ($endpoint in $Endpoints) {
            $url = "$baseUrl$endpoint"
            
            try {
                $response = Invoke-WebRequest -Uri $url -Method GET -TimeoutSec 5 -UseBasicParsing
                Write-Result -Success $true -Message "Endpoint $endpoint: OK (Status: $($response.StatusCode))"
                
                # Sprawdzenie formatu odpowiedzi dla /api/mobile-config
                if ($endpoint -eq "/api/mobile-config") {
                    try {
                        $content = $response.Content | ConvertFrom-Json
                        if ($content.PSObject.Properties.Name -contains "config") {
                            Write-Result -Success $true -Message "  Format danych: POPRAWNY (znaleziono klucz 'config')"
                        } else {
                            Write-Result -Success $false -Message "  Format danych: NIEPOPRAWNY (brak klucza 'config')"
                        }
                    } catch {
                        Write-Result -Success $false -Message "  Nie można sparsować odpowiedzi JSON: $_"
                    }
                }
            } catch [System.Net.WebException] {
                $statusCode = if ($_.Exception.Response) { $_.Exception.Response.StatusCode.Value__ } else { "n/d" }
                Write-Result -Success $false -Message "Endpoint $endpoint: BŁĄD (Status: $statusCode, Błąd: $($_.Exception.Message))"
            } catch {
                Write-Result -Success $false -Message "Endpoint $endpoint: BŁĄD ($($_.Exception.Message))"
            }
        }
        
        Write-Host ""
    }
}

# Sprawdza konfigurację usług Windows
function Test-WindowsServices {
    Write-Header "USŁUGI SIECIOWE WINDOWS"
    
    $services = @(
        "LanmanServer",    # Udostępnianie plików SMB
        "LanmanWorkstation", # Klient SMB
        "Dnscache",        # Usługa klienta DNS
        "nsi",             # Interfejs usługi sieciowej
        "iphlpsvc"         # Pomoc IP
    )
    
    foreach ($serviceName in $services) {
        try {
            $service = Get-Service -Name $serviceName -ErrorAction Stop
            $status = $service.Status
            $color = if ($status -eq "Running") { "Green" } else { "Yellow" }
            
            Write-Host "Usługa $($service.DisplayName) ($serviceName): $status" -ForegroundColor $color
        } catch {
            Write-Host "Usługa $serviceName: Nie znaleziono" -ForegroundColor Red
        }
    }
}

# Funkcja generująca raport diagnostyczny
function Export-DiagnosticReport {
    param (
        [string] $OutputFile = "diagnostyka_sieci_$(Get-Date -Format 'yyyyMMdd-HHmmss').txt"
    )
    
    Write-Header "GENEROWANIE RAPORTU DIAGNOSTYCZNEGO"
    
    try {
        # Przekierowujemy wyjście do pliku
        Start-Transcript -Path $OutputFile -Force
        
        # Uruchamiamy wszystkie testy
        Write-Host "RAPORT DIAGNOSTYKI SIECI - $(Get-Date)`n" -ForegroundColor Magenta
        
        Get-SystemInfo
        Test-NetworkConfiguration
        Test-FirewallServices
        Test-ApplicationPorts
        Test-ApiEndpoints
        Test-WindowsServices
        
        Write-Header "KONIEC RAPORTU"
        
        Stop-Transcript
        
        Write-Host "Raport zapisany do pliku: $OutputFile" -ForegroundColor Green
    } catch {
        Write-Host "Błąd podczas generowania raportu: $_" -ForegroundColor Red
    }
}

# Główna część skryptu
try {
    Write-Host "Diagnostyka sieci dla aplikacji Lista Obecności" -ForegroundColor Magenta
    Write-Host "------------------------------------------------`n" -ForegroundColor Magenta
    
    # Pobieramy lokalne adresy IP
    $localIPs = @(Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -ne "127.0.0.1" })
    $ipAddresses = $localIPs | ForEach-Object { $_.IPAddress }
    
    # Dodajemy lokalne adresy do testów
    $hostsToTest = @("localhost", "127.0.0.1") + $ipAddresses
    
    # Uruchamiamy testy
    Get-SystemInfo
    Test-NetworkConfiguration
    Test-FirewallServices
    Test-ApplicationPorts -Hosts $hostsToTest
    Test-ApiEndpoints -ApiUrls ($hostsToTest | ForEach-Object { "http://$_:8000", "http://$_:8002" })
    Test-WindowsServices
    
    $generateReport = Read-Host "`nCzy wygenerować szczegółowy raport diagnostyczny? (T/N)"
    if ($generateReport -eq "T" -or $generateReport -eq "t") {
        Export-DiagnosticReport
    }
    
    Write-Host "`nDiagnostyka zakończona. Sprawdź wyniki powyżej." -ForegroundColor Magenta
    
} catch {
    Write-Host "Wystąpił błąd podczas wykonywania diagnostyki: $_" -ForegroundColor Red
}

# Czekamy na naciśnięcie klawisza przed zakończeniem
Write-Host "`nNaciśnij dowolny klawisz, aby zakończyć..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
