# Sets the main company's country and currency from config/accounting.json, before l10n_de
# is installed (the chart of accounts is loaded for the company's country). Touches only
# country_id and currency_id on the main company - nothing else.
import json
import os

repo_root = os.environ["REPO_ROOT"]
config_path = os.path.join(repo_root, "config", "accounting.json")
if not os.path.isfile(config_path):
    raise FileNotFoundError(f"Missing required config file: {config_path}")

with open(config_path, encoding="utf-8") as f:
    accounting_config = json.load(f)

country_code = accounting_config["country_code"]
currency_code = accounting_config["currency_code"]

company = env["res.company"].search([], limit=1)
if not company:
    raise RuntimeError("No res.company record found.")

country = env["res.country"].search([("code", "=", country_code)], limit=1)
if not country:
    raise RuntimeError(f"No res.country found for country_code={country_code!r}")

currency = env["res.currency"].with_context(active_test=False).search([("name", "=", currency_code)], limit=1)
if not currency:
    raise RuntimeError(f"No res.currency found for currency_code={currency_code!r}")

changes = {}
if company.country_id.id != country.id:
    changes["country_id"] = country.id
if company.currency_id.id != currency.id:
    if not currency.active:
        currency.active = True
    changes["currency_id"] = currency.id

if changes:
    company.write(changes)
    env.cr.commit()
    print(f"Updated company {company.name!r}: {changes}")
else:
    print("no changes")
