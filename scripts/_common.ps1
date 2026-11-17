# Shared helpers for the scripts in this folder. Dot-source this file; do not run it directly.
# Compatible with Windows PowerShell 5.1 and PowerShell 7 - no ternary/null-coalescing operators.

function Get-HealthyMedEnv {
    param(
        [string]$EnvFile
    )

    $repoRoot = Split-Path -Parent $PSScriptRoot

    if (-not $EnvFile) {
        $EnvFile = Join-Path $repoRoot ".env"
    }

    if (-not (Test-Path $EnvFile)) {
        throw "Missing env file: $EnvFile. Copy .env.example to .env and fill in real local paths first."
    }

    $values = @{}
    Get-Content $EnvFile | ForEach-Object {
        $line = $_.Trim()
        if ($line.Length -eq 0 -or $line.StartsWith("#")) {
            return
        }
        $parts = $line -split "=", 2
        if ($parts.Count -eq 2) {
            $values[$parts[0].Trim()] = $parts[1].Trim()
        }
    }

    $required = @("ODOO_ROOT", "REPO_ROOT", "ODOO_CONF", "VENV_PATH", "DB_NAME", "ODOO_PORT")
    foreach ($key in $required) {
        if (-not $values.ContainsKey($key) -or $values[$key] -eq "") {
            throw "Missing required key '$key' in $EnvFile"
        }
    }

    $values["ODOO_BIN"] = Join-Path $values["ODOO_ROOT"] "odoo-bin"
    $values["PYTHON_EXE"] = Join-Path $values["VENV_PATH"] "Scripts\python.exe"

    $pathKeys = @("ODOO_ROOT", "REPO_ROOT", "ODOO_CONF", "VENV_PATH", "ODOO_BIN", "PYTHON_EXE")
    foreach ($pathKey in $pathKeys) {
        if (-not (Test-Path $values[$pathKey])) {
            throw "Path for '$pathKey' does not exist: $($values[$pathKey])"
        }
    }

    return $values
}
