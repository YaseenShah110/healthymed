# Bootstrap scripts

Numbered Python files in this folder run in order (via `scripts\bootstrap.ps1`),
each executed inside `odoo-bin shell` against the main database. The `env`
(odoo.api.Environment) and `odoo` globals are already available - do not
import `odoo.cli` or start your own environment.

Rules:
- **Idempotent.** Running a script a second time must change nothing, and it
  must print `no changes` when there is nothing left to do.
- **Fail loudly.** If required config (an environment variable or a
  `config\*.json` file) is missing, raise an error - never skip silently.
- **Numeric prefix.** Name files `00_`, `10_`, `20_`, ... so filename order is
  execution order.
- Config paths (`REPO_ROOT`, `ODOO_CONF`, `DB_NAME`) are available via
  `os.environ`, set by `scripts\bootstrap.ps1` before each script runs.
