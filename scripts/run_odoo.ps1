# Starts Odoo locally using paths from .env (see .env.example).
param(
    [string]$EnvFile
)

. (Join-Path $PSScriptRoot "_common.ps1")
$cfg = Get-HealthyMedEnv -EnvFile $EnvFile

Write-Host "Starting Odoo:"
Write-Host "  python : $($cfg.PYTHON_EXE)"
Write-Host "  bin    : $($cfg.ODOO_BIN)"
Write-Host "  config : $($cfg.ODOO_CONF)"
Write-Host "  db     : $($cfg.DB_NAME)"
Write-Host "  port   : $($cfg.ODOO_PORT)"

& $cfg.PYTHON_EXE $cfg.ODOO_BIN -c $cfg.ODOO_CONF
