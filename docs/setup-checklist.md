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
