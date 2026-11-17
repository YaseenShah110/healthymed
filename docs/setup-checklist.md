# Manual setup steps (not scripted)

These are one-time, machine-specific steps the scripts in `scripts\` do not and
should not automate.

1. **Copy `.env.example` to `.env`** and fill in the real local paths
   (`ODOO_ROOT`, `REPO_ROOT`, `ODOO_CONF`, `VENV_PATH`, `DB_NAME`,
   `ODOO_PORT`). `.env` is gitignored - everyone sets their own.
2. **Copy `odoo.conf.example` to `odoo.conf`** and fill in real database
   credentials. `odoo.conf` is gitignored and must never be committed.
3. **Odoo venv must already exist** at the path `.env`'s `VENV_PATH` points
   to, with Odoo's own `requirements.txt` installed. These scripts don't
   create or provision the venv.
4. **Install `phonenumbers` into that venv** if it is missing:
   `<venv>\Scripts\python.exe -m pip install phonenumbers`.
   It is an external dependency of `account_peppol` (auto-installed
   alongside `l10n_de`) and of `phone_validation` (used by `crm`), but it
   is missing from Odoo 19's own `requirements.txt`, so a fresh venv will
   need it installed manually before `scripts\bootstrap.ps1` can finish.
5. **Install `ruff`** for whichever Python runs the linter (it is not part
   of the Odoo venv): `python -m pip install --user ruff`.
6. **Database `healthymed` must already exist** in Postgres before running
   any script here; these scripts don't create it.
7. Run `scripts\bootstrap.ps1` only while **no other Odoo process is bound
   to the same database** (stop `scripts\run_odoo.ps1` first) - `odoo-bin
   shell` and the HTTP server can both reach the DB, but installing modules
   while the web server also holds the old registry in memory is avoidable
   risk, not a hard requirement.
8. **Copy `config\company.json.example` to `config\company.json`** and fill
   in the real company data yourself - the bootstrap script (`30_company.py`)
   never invents or copies values from other documents; it only fails loudly
   if a required key is missing. `config\company.json` is gitignored.
9. If a real logo file is available, put it under `data_private\` (gitignored)
   and point `logo_path` at it (relative to the repo root). If there is no
   logo file yet, leave `logo_path` empty/missing - `30_company.py` skips the
   logo and says so, it does not fail.
10. **Document layout confirmed (2026-11-17):** keep the layout Odoo already
    auto-selected when `l10n_de`/`l10n_din5008` were installed - no setting
    change needed. Settings → General Settings → Companies → (company) →
    Configure Document Layout:
    - Layout: `l10n_din5008.external_layout_din5008` (DIN 5008 Type B)
    - Paper format: "European A4 for DIN5008 Type B" - A4 portrait, margins
      top 45mm / bottom 40mm / left 20mm / right 10mm
    - Font: Lato
    - Background: Blank
    This was a deliberate confirmation, not an unexamined default - recorded
    here so nobody "fixes" it later by accident.
11. `legal_name` in `config\company.json` has no corresponding Odoo 19 field
    (verified against `base`, `account`, `l10n_de` - none add one). It is
    required in the config file for documentation only; `30_company.py`
    never writes it anywhere in Odoo.
