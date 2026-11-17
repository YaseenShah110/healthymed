# Installs the modules listed in config/apps.json that are not installed yet, using the
# same ORM method Odoo's own Apps UI uses (button_immediate_install). Installs nothing
# that is not on that list. Demo data is off by default in Odoo (--with-demo defaults to
# False), matching this database's existing state.
import json
import os

repo_root = os.environ["REPO_ROOT"]
config_path = os.path.join(repo_root, "config", "apps.json")
if not os.path.isfile(config_path):
    raise FileNotFoundError(f"Missing required config file: {config_path}")

with open(config_path, encoding="utf-8") as f:
    app_names = json.load(f)

modules = env["ir.module.module"].search([("name", "in", app_names)])
found_names = set(modules.mapped("name"))
missing = sorted(set(app_names) - found_names)
if missing:
    raise RuntimeError(f"Modules not found in this Odoo install: {missing}")

already_installed = modules.filtered(lambda m: m.state == "installed")
to_install = modules.filtered(lambda m: m.state == "uninstalled")
other_states = modules - already_installed - to_install

if other_states:
    raise RuntimeError(
        "Modules in an unexpected state (not 'installed' or 'uninstalled'): "
        f"{[(m.name, m.state) for m in other_states]}"
    )

if to_install:
    to_install.button_immediate_install()
    env.cr.commit()
    print("Installed:", sorted(to_install.mapped("name")))
else:
    print("Installed: (none - nothing to do)")

print("Already installed:", sorted(already_installed.mapped("name")))

if not to_install:
    print("no changes")
