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

## Task 4: what SKR04 created (read-only inspection, 2026-11-17)

Field names verified in `C:\odoo\odoo19\addons\account\models\account_tax.py`
and `...\models\partner.py` before reading anything - not guessed.

- **Taxes (`account.tax`):** SKR04 ships ~50 sale/purchase taxes across 6 tax
  groups (`VAT 0%`, `VAT 5,5%`, `VAT 7%`, `VAT 10,7%`, `VAT 19%`, `VAT x%`).
  Most are inactive by default; only the domestic/EU ones Odoo pre-activates
  are `active=True` (e.g. `19%`, `7%`, `0%`, `0% EU D`, `19% EU D`, `0% EX`
  for sale; `19% I`, `7% I`, `19% EU`, `19% EU O S`, `7% EU`, `19% EX` for
  purchase). `tax_scope` is unset (`False`) on all of them.
- **Company default taxes:** `res.company.account_sale_tax_id` /
  `.account_purchase_tax_id` are **already set** by the SKR04 chart load (not
  by us) to `19%` (sale) and `19% I` (purchase) - i.e. the standard German
  domestic rate, both ways.
- **Disambiguating key for Task 4:** `type_tax_use` + `amount` is ambiguous
  for purchase - there are 4 active taxes at 19% purchase (`19% I`, `19% EU`,
  `19% EU O S`, `19% EX`). The field that cleanly picks out the domestic one
  without referencing it by name is `l10n_de_datev_code` (the German DATEV
  export code): sale `19%` → datev code `3`, purchase `19% I` → datev code
  `9`. Confirmed unique per code via direct DB query. This is the standard
  German accounting convention (DATEV codes), not an arbitrary tiebreaker.
- **Fiscal positions (`account.fiscal.position`):** 6 positions, same as
  Task 2's summary. Odoo 19 changed how the tax mapping works from older
  versions: `fiscal_position.tax_ids` (Many2many) lists the *destination*
  taxes; each destination tax's own `original_tax_ids` field says which
  tax(es) it replaces. There is no `account.fiscal.position.tax` src/dest
  line model anymore - only `account.fiscal.position.account` still works
  that way (`account_src_id` → `account_dest_id`).
- **Journals (`account.journal`):** Sales (`INV`), Purchases (`BILL`), Bank
  (`BNK1`), Miscellaneous Operations, Cash Basis Taxes, Exchange Difference,
  Inventory Valuation (`STJ`). Sales/Purchases/Bank have a
  `default_account_id`; the rest don't.
- **Company default accounts:** `income_account_id`=`4400`,
  `expense_account_id`=`5400` (direct `res.company` fields). Receivable/payable
  are `res.partner.property_account_receivable_id`/`property_account_payable_id`
  - company-dependent fields, not plain company fields; their *default* value
  (no specific partner) is `1205` / `3301`, read the same way Odoo's own code
  does it: `field.get_company_dependent_fallback(records)` (backed by
  `ir.default`, not the old `ir.property` mechanism).

## Task 4: taxes/payment terms - manual steps and where to check (2026-11-17)

1. **Copy `config\payment_terms.json.example` to `config\payment_terms.json`**
   and fill in the real terms yourself (name + schedule per entry).
   `45_payment_terms.py` never invents any; it only fails loudly if the file
   is missing. `config\payment_terms.json` is gitignored.
2. `config\accounting.json` now also needs `default_sale_tax` /
   `default_purchase_tax` (each a dict of `account.tax` field/value pairs that
   uniquely identify one tax - see the DATEV-code note above for why `amount`
   alone isn't enough for this chart).
3. Fiscal positions and bank journals were **reported only, not changed** -
   see `docs/decisions.md` for the user's confirmation on both.
4. **Where to see it in the UI:**
   - Default taxes: Settings → Accounting → (scroll to) Default Taxes, or
     Accounting → Configuration → Settings.
   - Payment terms: Accounting → Configuration → Payment Terms.
   - Journals: Accounting → Configuration → Journals.
   - The manual invoice check: Accounting → Customer Invoices - any posted
     invoice with product "TASK4-CHECK Service" (archived after the script
     runs, so search with the Archived filter on) shows the same untaxed
     amount / tax / total / accounts the script printed. The script's own
     test invoice is left **cancelled** (not deletable once posted - see
     `docs/decisions.md`), so it will show up there too unless filtered out.
5. **Manual invoice check, by hand:** Accounting → Customer Invoices → New,
   pick any customer, add a line with a product that has the default 19%
   sale tax, confirm the invoice shows 19% tax and posts to account `3806`
   (tax) / the product's income account (defaults to `4400` unless the
   product category overrides it).
