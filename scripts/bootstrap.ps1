# Runs every scripts\bootstrap\*.py file, in numeric filename order, through "odoo-bin shell"
# against the main database. Config paths are passed to each script via environment variables
# (REPO_ROOT, ODOO_CONF, DB_NAME) rather than command-line args.
param(
    [string]$EnvFile
)

. (Join-Path $PSScriptRoot "_common.ps1")
$cfg = Get-HealthyMedEnv -EnvFile $EnvFile

$bootstrapDir = Join-Path $PSScriptRoot "bootstrap"
$scripts = Get-ChildItem -Path $bootstrapDir -Filter "*.py" | Sort-Object Name

if ($scripts.Count -eq 0) {
    Write-Host "No bootstrap scripts found in $bootstrapDir"
    exit 0
}

$env:REPO_ROOT = $cfg.REPO_ROOT
$env:ODOO_CONF = $cfg.ODOO_CONF
$env:DB_NAME = $cfg.DB_NAME

foreach ($script in $scripts) {
    Write-Host ""
    Write-Host "=== Running $($script.Name) ==="
    # Redirect via cmd.exe (real file-handle stdin), not a PowerShell pipe - piping a
    # string to a native exe re-encodes it and prepends a UTF-8 BOM, which breaks
    # Python's exec() of the piped script.
    $cmdLine = '"' + $cfg.PYTHON_EXE + '" "' + $cfg.ODOO_BIN + '" shell -c "' + $cfg.ODOO_CONF + `
        '" -d ' + $cfg.DB_NAME + ' --no-http < "' + $script.FullName + '"'
    cmd /c $cmdLine
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Bootstrap script $($script.Name) failed with exit code $LASTEXITCODE"
        exit $LASTEXITCODE
    }
}
