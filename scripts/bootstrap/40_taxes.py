# Sets the company's default sale/purchase taxes from config/accounting.json, through
# the correct Odoo 19 mechanism: res.company.account_sale_tax_id / .account_purchase_tax_id
# (verified in C:\odoo\odoo19\addons\account\models\company.py). Never references a tax
# by name or database ID - only by the structural keys given in the config file.
import json
import os

repo_root = os.environ["REPO_ROOT"]
config_path = os.path.join(repo_root, "config", "accounting.json")
if not os.path.isfile(config_path):
    raise FileNotFoundError(f"Missing required config file: {config_path}")

with open(config_path, encoding="utf-8") as f:
    cfg = json.load(f)

for required_key in ("default_sale_tax", "default_purchase_tax"):
    if required_key not in cfg:
        raise RuntimeError(f"Missing required key {required_key!r} in {config_path}")


def find_tax(spec, company_id):
    domain = [(key, "=", value) for key, value in spec.items()] + [("company_id", "=", company_id)]
    taxes = env["account.tax"].with_context(active_test=False).search(domain)
    if len(taxes) != 1:
        raise RuntimeError(f"Expected exactly one account.tax matching {spec!r}, found {len(taxes)}")
    return taxes


company = env["res.company"].search([], limit=1)
if not company:
    raise RuntimeError("No res.company record found.")

sale_tax = find_tax(cfg["default_sale_tax"], company.id)
purchase_tax = find_tax(cfg["default_purchase_tax"], company.id)

diff = {}
if company.account_sale_tax_id.id != sale_tax.id:
    diff["account_sale_tax_id"] = sale_tax.id
if company.account_purchase_tax_id.id != purchase_tax.id:
    diff["account_purchase_tax_id"] = purchase_tax.id

if diff:
    company.write(diff)
    env.cr.commit()
    print("Changed:", diff)
else:
    print("no changes")
