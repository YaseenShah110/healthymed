# Decisions

| Date | Decision | Why |
|---|---|---|
| 2026-11-17 | Install exactly these 12 modules for Task 2, recorded in `config/apps.json`: `sale_management`, `purchase`, `stock`, `account`, `delivery`, `stock_dropshipping`, `product_expiry`, `website_sale`, `crm`, `l10n_de`, `payment_stripe`, `payment_paypal`. | Matches the module list given for this task; all 12 names verified to exist as-is in Odoo 19 core (`C:\odoo\odoo19\addons`) - no renames needed. |
| 2026-11-17 | Keep `crm` in the install list even though `docs/scope.md` does not explicitly request a CRM app. | The module list is "the senior's system"; `scope.md` section 4 explicitly says fields/models the senior built beyond the contract "are still built, to match the senior's project." `crm` is treated the same way: beyond-contract, kept for parity with the senior's reference build. |
| 2026-11-17 | Chart template code for the German chart of accounts is `de_skr04`, not a guess. | Found in `C:\odoo\odoo19\addons\l10n_de\models\template_de_skr04.py` (`@template('de_skr04')`). Loaded via the standard public API `env["account.chart.template"].try_loading("de_skr04", company=company, install_demo=False)`, defined in `C:\odoo\odoo19\addons\account\models\chart_template.py`. `de_skr03` (SKR03) exists alongside it in the same module and must never be loaded instead. |
| 2026-11-17 | Installed `phonenumbers` into the Odoo venv (`C:\odoo\odoo19\venv`) via pip. | Required by `account_peppol` (auto-installed alongside `l10n_de`) and `phone_validation` (used by `crm`), but missing from Odoo 19's own `requirements.txt`. Installing the package is environment setup, not an edit to Odoo core code. |
| 2026-11-17 | Company country/currency set from `config/accounting.json` (`DE`/`EUR`) before any module install, touching only `country_id` and `currency_id` on the main company. | The chart of accounts loads for the company's country; l10n_de needs the company already on Germany/EUR. No other company field was touched. |
| 2026-11-17 | `legal_name` in `config/company.json` is documentation-only and is never written to Odoo. | No field in `base`, `account` or `l10n_de` corresponds to a separate legal/trading name distinct from `res.company.name` - grepped core, found nothing. Asked the user rather than guessing. |
| 2026-11-17 | No bank account / IBAN in `config/company.json` or `30_company.py`. | User confirmed it is out of scope for this task. |
| 2026-11-17 | Document layout kept as the DIN 5008 Type B default Odoo already auto-selected when `l10n_de`/`l10n_din5008` were installed - no setting change applied. | User confirmed this matches the senior's system: layout `l10n_din5008.external_layout_din5008`, paper format "European A4 for DIN5008 Type B" (A4 portrait, margins 45/40/20/10mm), font Lato, background Blank. |
| 2026-11-17 | Language activation uses Odoo's own `base.language.install` wizard (`lang_install()`), which also loads translations for every installed module via `ir.module.module._update_translations`. | Found in `C:\odoo\odoo19\odoo\addons\base\wizard\base_language_install.py` - this is the same method the Settings UI uses, not a hand-rolled translation loader. |
| 2026-11-17 | `config/company.json` real values (name, address, VAT, language, timezone) came from the user, who read them read-only off staging's `res.company`/admin user and explicitly confirmed each one for use here. `email`, `phone`, `website`, `street2`, `state_id`, `company_registry` are genuinely blank on staging, not omitted. | Matches the standing rule: never invent or copy values without the user's confirmation. User supplied and confirmed; not copied unilaterally. |
| 2026-11-17 | Logo skipped for now (`logo_path` left empty in `config/company.json`). | Staging has a logo set, but user chose "skip for now" rather than fetch it immediately. `30_company.py` already handles a missing logo cleanly (prints and skips, does not fail). Add later by placing a file under `data_private\` and setting `logo_path`. |
| 2026-11-17 | Fiscal positions (Task 4): not touched, no changes made or planned. | User confirmed the senior's system also left the 6 standard SKR04 fiscal positions as Odoo's defaults. |
| 2026-11-17 | No bank journal/IBAN configured (Task 4). | User confirmed the scope does not need one yet; journals are only reported, not created or modified. |
| 2026-11-17 | Default tax lookup in `config/accounting.json` uses `l10n_de_datev_code` (German DATEV export code: `3` sale, `9` purchase) as the disambiguating key, not `name` or a database ID. | `type_tax_use` + `amount` alone is ambiguous: 4 active taxes are at 19% purchase (`19% I`, `19% EU`, `19% EU O S`, `19% EX`). `l10n_de_datev_code` is unique per tax and is a real German accounting convention field, not an arbitrary tiebreaker - confirmed via direct query that codes `3`/`9` each match exactly one tax. |
| 2026-11-17 | `scripts/checks/invoice_check.py` cancels the posted move and archives (`active=False`) the product/partner it created, rather than deleting them. | A posted journal entry sets `posted_before=True` permanently (even after cancelling), which blocks `unlink()` on it and its chatter to protect the audit trail; the product/partner it references then can't be deleted either (FK restrict from `account_move_line`). The task explicitly allows "deletes or cancels" for exactly this reason. Separately: `odoo-bin shell` (`odoo/cli/shell.py`) calls `cr.rollback()` both before and after the console session, so since the script never calls `env.cr.commit()`, nothing from it persists anyway once the shell process exits - confirmed empirically (`account_move` table is empty after 3 runs). The explicit cancel/archive cleanup is kept as a second, explicit guarantee rather than relying only on that implicit behavior. |
| 2026-11-17 | Default taxes (`19%` sale / `19% I` purchase, DATEV `3`/`9`) confirmed correct by the user from staging's live `account_sale_tax_id`/`account_purchase_tax_id` - no correction needed, `40_taxes.py` reports "no changes" since the SKR04 load had already set them. | Same standing rule: user confirmed from staging read-only, not invented. |
| 2026-11-17 | Payment terms: the 10 real terms from staging (listed in full in `config/payment_terms.json`, gitignored) are Odoo's own stock demo terms, none customized for HealthyMed. There is **no "14 Days" term** - the example key in `payment_terms.json.example` was illustrative only; real terms use `15 Days`/`21 Days` instead. | User provided the exact list read-only from staging and explicitly flagged the "14 Days" mismatch rather than letting it be assumed. |
| 2026-11-17 | `45_payment_terms.py` matches `account.payment.term.line.days_next_month` against Odoo's own field default (`'10'`), not against `False`, when a line's JSON doesn't specify that key. | Found a real idempotency bug: that field defaults to `'10'` on every line regardless of `delay_type` (it's only hidden in the UI for other delay types, not actually blank in the DB). Comparing against `False` made every line without an explicit `days_next_month` look "changed" on every run. Fixed, then verified two consecutive runs both report "no changes" for all 10 terms. |

## Open question (Task 3)

Inspecting `website.website` via `odoo-bin shell` raised `KeyError` even
though the `website` module is installed and the `website` Postgres table has
a row (`id=1, name='My Website'`). Not blocking (favicon is not a Task 3
config key), but worth someone checking if it ever matters - might be a
registry quirk specific to the `--no-http` shell session.

## Notes on Task 2 scope

Nothing in Odoo 19 core required a rename from the original module list - all
12 names matched exactly.

`docs/decisions.md` and the rest of Task 0's "governance" deliverables
(`field-spec.json`, `module-map.md`, `scope-matrix.md`, the broader "Open
questions" list) were not finished when this task started; this file was
created fresh here with only the decisions this task (Task 2) made. The
Task 0 open-questions list is still pending separately.
