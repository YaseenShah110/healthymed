# Read-only sanity check: Odoo version, installed module count, main company name.
# Changes nothing.
import odoo

installed_count = env["ir.module.module"].search_count([("state", "=", "installed")])
company = env["res.company"].search([], limit=1)

print("Odoo version:", odoo.release.version)
print("Installed modules:", installed_count)
print("Company:", company.name if company else "(none)")
print("no changes")
