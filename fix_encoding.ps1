# Skrypt do naprawy kodowania polskich znaków w plikach HTML
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$files = @(
    "attendance_day.html",
    "attendance_summary.html", 
    "employee_add.html",
    "employee_edit.html",
    "employee_details.html",
    "mobile_config.html",
    "pin_access_monitor.html",
    "time_rounding.html"
)

$replacements = @{
    "ZaokrÄ…glanie" = "Zaokrąglanie"
    "ZarzÄ…dzanie" = "Zarządzanie"
    "zespoÅ‚em" = "zespołem"
    "ObecnoÅ›ci" = "Obecności"
    "wejÅ›Ä‡" = "wejść"
    "wyjÅ›Ä‡" = "wyjść"
    "pracownikÃ³w" = "pracowników"
    "wÅ‚Ä…czone" = "włączone"
    "takÅ¼e" = "także"
    "bÄ™dzie" = "będzie"
    "wyÅ‚Ä…czone" = "wyłączone"
    "dokÅ‚adnie" = "dokładnie"
    "âš ï¸" = "⚠️"
    "â†'" = "→"
}

foreach ($file in $files) {
    $fullPath = "m:\Programowanie\lista_obecnosci\frontend\$file"
    if (Test-Path $fullPath) {
        Write-Host "Naprawiam kodowanie w: $file"
        $content = Get-Content $fullPath -Raw -Encoding UTF8
        
        foreach ($key in $replacements.Keys) {
            $content = $content.Replace($key, $replacements[$key])
        }
        
        # Dodaj brakujący link do zarządzania wersjami jeśli go nie ma
        if ($content -notmatch "app_version_management\.html") {
            $oldPattern = '            <a href="time_rounding.html"([^>]*)>\s*<i class="fas fa-clock"></i> Zaokrąglanie Czasu Pracy\s*</a>\s*</div>'
            $newPattern = '            <a href="time_rounding.html"$1>
              <i class="fas fa-clock"></i> Zaokrąglanie Czasu Pracy
            </a>
            <a href="app_version_management.html">
              <i class="fas fa-sync-alt"></i> Zarządzanie Wersjami
            </a>
          </div>'
            $content = $content -replace $oldPattern, $newPattern
        }
        
        Set-Content $fullPath -Value $content -Encoding UTF8
    }
}
