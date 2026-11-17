# Decisions

| Date | Decision | Why |
|---|---|---|
| 2026-11-17 | Install exactly these 12 modules for Task 2, recorded in `config/apps.json`: `sale_management`, `purchase`, `stock`, `account`, `delivery`, `stock_dropshipping`, `product_expiry`, `website_sale`, `crm`, `l10n_de`, `payment_stripe`, `payment_paypal`. | Matches the module list given for this task; all 12 names verified to exist as-is in Odoo 19 core (`C:\odoo\odoo19\addons`) - no renames needed. |
| 2026-11-17 | Keep `crm` in the install list even though `docs/scope.md` does not explicitly request a CRM app. | The module list is "the senior's system"; `scope.md` section 4 explicitly says fields/models the senior built beyond the contract "are still built, to match the senior's project." `crm` is treated the same way: beyond-contract, kept for parity with the senior's reference build. |
| 2026-11-17 | Chart template code for the German chart of accounts is `de_skr04`, not a guess. | Found in `C:\odoo\odoo19\addons\l10n_de\models\template_de_skr04.py` (`@template('de_skr04')`). Loaded via the standard public API `env["account.chart.template"].try_loading("de_skr04", company=company, install_demo=False)`, defined in `C:\odoo\odoo19\addons\account\models\chart_template.py`. `de_skr03` (SKR03) exists alongside it in the same module and must never be loaded instead. |
| 2026-11-17 | Installed `phonenumbers` into the Odoo venv (`C:\odoo\odoo19\venv`) via pip. | Required by `account_peppol` (auto-installed alongside `l10n_de`) and `phone_validation` (used by `crm`), but missing from Odoo 19's own `requirements.txt`. Installing the package is environment setup, not an edit to Odoo core code. |
| 2026-11-17 | Company country/currency set from `config/accounting.json` (`DE`/`EUR`) before any module install, touching only `country_id` and `currency_id` on the main company. | The chart of accounts loads for the company's country; l10n_de needs the company already on Germany/EUR. No other company field was touched. |

## Notes on Task 2 scope

Nothing in Odoo 19 core required a rename from the original module list - all
12 names matched exactly.

`docs/decisions.md` and the rest of Task 0's "governance" deliverables
(`field-spec.json`, `module-map.md`, `scope-matrix.md`, the broader "Open
questions" list) were not finished when this task started; this file was
created fresh here with only the decisions this task (Task 2) made. The
Task 0 open-questions list is still pending separately.
