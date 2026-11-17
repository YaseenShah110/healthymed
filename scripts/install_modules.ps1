# Installs the given modules with --stop-after-init, then shows ERROR/WARNING lines from the run.
param(
    [Parameter(Mandatory = $true)]
    [string[]]$Modules,
    [string]$EnvFile
)

. (Join-Path $PSScriptRoot "_common.ps1")
$cfg = Get-HealthyMedEnv -EnvFile $EnvFile

$moduleArg = $Modules -join ","
Write-Host "Installing modules: $moduleArg"

$output = & $cfg.PYTHON_EXE $cfg.ODOO_BIN -c $cfg.ODOO_CONF -d $cfg.DB_NAME -i $moduleArg --stop-after-init --no-http 2>&1
$output | ForEach-Object { Write-Host $_ }

$problems = $output | Select-String -Pattern "ERROR|WARNING"
Write-Host ""
if ($problems) {
    Write-Host "=== ERROR/WARNING lines ==="
    $problems | ForEach-Object { Write-Host $_.Line }
}
else {
    Write-Host "No ERROR or WARNING lines found."
}
