# Loads the German SKR04 chart of accounts for the main company (template code
# "de_skr04", registered in l10n_de/models/template_de_skr04.py, loaded through the
# standard account.chart.template.try_loading() API). Refuses to touch a company that
# already has a different chart with posted journal items, skips if SKR04 is already
# loaded, and never loads SKR03.
import json
import os

repo_root = os.environ["REPO_ROOT"]
config_path = os.path.join(repo_root, "config", "accounting.json")
if not os.path.isfile(config_path):
    raise FileNotFoundError(f"Missing required config file: {config_path}")

with open(config_path, encoding="utf-8") as f:
    accounting_config = json.load(f)

chart_template = accounting_config["chart_template"]
if chart_template == "de_skr03":
    raise RuntimeError("Refusing to load de_skr03: SKR04 is required, not SKR03.")

company = env["res.company"].search([], limit=1)
if not company:
    raise RuntimeError("No res.company record found.")

if company.chart_template and company.chart_template != chart_template:
    posted_count = env["account.move"].search_count(
        [("company_id", "=", company.id), ("state", "=", "posted")]
    )
    if posted_count:
        raise RuntimeError(
            f"Company {company.name!r} already has chart_template={company.chart_template!r} "
            f"with {posted_count} posted journal item(s). Refusing to change the chart."
        )

if company.chart_template == chart_template:
    print("no changes")
else:
    env["account.chart.template"].try_loading(chart_template, company=company, install_demo=False)
    env.cr.commit()
    print(f"Loaded chart template {chart_template!r} for company {company.name!r}")

accounts = env["account.account"].search([("company_ids", "in", company.id)])
sale_taxes = env["account.tax"].search([("company_id", "=", company.id), ("type_tax_use", "=", "sale")])
purchase_taxes = env["account.tax"].search([("company_id", "=", company.id), ("type_tax_use", "=", "purchase")])
fiscal_positions = env["account.fiscal.position"].search([("company_id", "=", company.id)])
journals = env["account.journal"].search([("company_id", "=", company.id)])

print(f"Accounts: {len(accounts)}")
print("Sale taxes:", [(t.name, t.amount) for t in sale_taxes])
print("Purchase taxes:", [(t.name, t.amount) for t in purchase_taxes])
print("Fiscal positions:", fiscal_positions.mapped("name"))
print("Journals:", [(j.name, j.type) for j in journals])
