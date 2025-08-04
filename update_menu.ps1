# Skrypt PowerShell do aktualizacji menu w plikach HTML
$files = @(
    "attendance_day.html",
    "attendance_summary.html", 
    "employee_add.html",
    "employee_edit.html",
    "employee_details.html",
    "employees.html",
    "mobile_config.html",
    "pin_access_monitor.html",
    "time_rounding.html"
)

$oldPattern = @"
            <a href="time_rounding.html">
              <i class="fas fa-clock"></i> Zaokrąglanie Czasu Pracy
            </a>
          </div>
"@

$newPattern = @"
            <a href="time_rounding.html">
              <i class="fas fa-clock"></i> Zaokrąglanie Czasu Pracy
            </a>
            <a href="app_version_management.html">
              <i class="fas fa-sync-alt"></i> Zarządzanie Wersjami
            </a>
          </div>
"@

foreach ($file in $files) {
    $fullPath = "m:\Programowanie\lista_obecnosci\frontend\$file"
    if (Test-Path $fullPath) {
        Write-Host "Aktualizuję: $file"
        $content = Get-Content $fullPath -Raw
        $newContent = $content.Replace($oldPattern, $newPattern)
        Set-Content $fullPath -Value $newContent -Encoding UTF8
    }
}
