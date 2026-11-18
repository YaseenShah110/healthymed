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

## Task 5: settings/website/mail - read-only inspection (2026-11-17)

`docs\module-map.md` still doesn't exist (Task 0 was never finished) - this
inspection uses `docs\scope.md` only. Field/group names verified in
`C:\odoo\odoo19\addons\{product,stock,stock_dropshipping,purchase_stock,
product_expiry,website}\models\res_config_settings.py` and
`website\models\website.py`, `odoo\addons\base\models\ir_mail_server.py` -
not from memory.

**Current `res.config.settings` values that matter here:**
| Field | Label | Current | Set by |
|---|---|---|---|
| `group_product_pricelist` | Pricelists | **False** | nothing yet |
| `group_stock_production_lot` | Lots & Serial Numbers | **True** | already on, module install side-effect |
| `module_product_expiry` | Expiration Dates | **True** | `product_expiry` installed in Task 2 |
| `module_stock_dropshipping` | Dropshipping | **True** | `stock_dropshipping` installed in Task 2 |
| `module_delivery` | Delivery Methods | **True** | `delivery` installed in Task 2 |
| `group_stock_multi_locations` | Storage Locations | **False** | nothing yet |
| `group_stock_adv_location` | Multi-Step Routes | **False** | nothing yet |

Note: there is **no settings field for "multiple warehouses"** at all in
Odoo 19 core - grepped `stock`'s entire `res_config_settings.py`, no
`group_stock_multi_warehouses` boolean exists. Creating more than one
`stock.warehouse` record needs no setting toggle; that's purely Task 6's job.
`group_stock_multi_locations` ("Storage Locations") is a different thing -
sub-locations inside a warehouse, not warehouse count.

**Website record (id=1, "My Website"):** `domain`=`False` (unset),
`default_lang_id`=`en_US`, `language_ids`=`['en_US']` only (German is active
as an Odoo language since Task 3, but not yet added to this website's
language list), `auth_signup_uninvited`=`'b2c'` (Free sign up - the two real
values are `'b2b'` "On invitation" and `'b2c'` "Free sign up"),
`cookies_bar`=`False`. None of these are touched by this inspection.

**Mail servers:** `ir.mail_server` count = 0, `fetchmail.server` count = 0 -
nothing configured yet.

## Task 6: warehouses - read-only inspection (2026-11-17)

Field names verified in `C:\odoo\odoo19\addons\stock\models\stock_warehouse.py`
and `stock_dropshipping\models\res_company.py` - not from memory.

**Current warehouses:** only **one** exists.
| Field | Value |
|---|---|
| `name` | "My Company" (Odoo's installer default - not yet renamed) |
| `code` | `WH` |
| `company_id` | HealthyMed |
| `reception_steps` | `one_step` |
| `delivery_steps` | `ship_only` |
| `active` | True |
| `view_location_id` | "WH" (usage=`view`) |
| `lot_stock_id` | "WH/Stock" (usage=`internal`) |

This is also the **default** warehouse (the only one, first by sequence).
`code` is `Char(size=5)` - **max 5 characters**, so both new warehouse codes
must fit that limit.

**Locations under it:** just `WH` (view) and `WH/Stock` (internal) - the
plain 1-step setup, nothing else.

**Operation types:** `Receipts` (incoming, Vendors → WH/Stock), `Delivery
Orders` (outgoing, WH/Stock → Customers), both tied to this warehouse; and
`Dropship` (code=`dropship`, **`warehouse_id` is empty/False** - not tied to
any warehouse at all, Vendors → Customers).

**Routes:** `Buy` (warehouse-scoped to "My Company"), `Dropship`
(`company_id` empty - shared across all companies, `warehouse_ids` empty -
not tied to any warehouse), plus the two auto-generated 1-step routes for
this warehouse's own receive/deliver.

**Dropship mechanism (verified in `stock_dropshipping/models/res_company.py`,
`_create_dropship_picking_type`/`_create_dropship_rule`):** created **once
per company**, not per warehouse. The picking type is created with
`'warehouse_id': False` explicitly. The rule uses only the virtual
`stock.stock_location_suppliers`/`stock.stock_location_customers` locations
- never a warehouse-specific location. **Conclusion: the supplier-handling
warehouse needs nothing special for dropshipping to work; the route is
warehouse-agnostic by design.** Not an open question - this is settled from
core source, not a guess.

## Task 8: healthymed_rollen - where to see it, manual check (2026-11-18)

1. **Fixed `odoo.conf`'s `addons_path`** to include the `addons\` subfolder
   (not just the repo root) - this is where `healthymed_rollen` and any
   future custom module actually live. If you set up a fresh `odoo.conf`
   from `odoo.conf.example`, it's already correct there.
2. **Where to see the roles in the UI:** Settings → Users & Companies →
   Users → open any user → the **HealthyMed-Rolle** section of the Access
   Rights area shows the four roles (Innendienst, Lager und Versand,
   Buchhaltung, Geschäftsführung) as one radio-style privilege, same as
   Sales/Inventory/etc.
3. **5-minute manual check (do this yourself - I won't create real users
   or store any password):**
   - Settings → Users & Companies → Users → New. Create one user per role
     with fake data (e.g. `test-innendienst@example.com`), pick its
     HealthyMed-Rolle role, save.
   - Repeat for all four roles.
   - Open a **private/incognito browser window**, log in as each test
     user, and confirm which top-level menus appear (Sales, Inventory,
     Invoicing, Purchase, Website) - compare against
     `scripts/checks/roles_check.py`'s table. Note: the **Website** menu
     will appear for every user regardless of role - it's gated only by
     the generic "internal user" group, not a Website-specific one (see
     `docs/decisions.md`).
   - Delete the four test users afterward, or leave them archived - your
     call, they're yours to manage since you created them by hand.
4. **Open mapping decisions** (not yet confirmed against the senior's
   system): which "Sales: User" level, which Website editor level, which
   Accounting groups - see `docs/decisions.md`. Check Settings → Technical
   → Groups there to confirm or correct, then edit
   `addons\healthymed_rollen\security\healthymed_rollen_groups.xml`
   (one `implied_ids` list per role) if anything needs to change.

## Task 9: healthymed_ssb - where to see it, manual check (2026-11-18)

1. **Where to see each field:**
   - Product form (any product) → General Information page → "Consultation
     Supply (SSB)" checkbox and "PZN" field, right after the Type field.
   - Products search → filter dropdown → "SSB".
   - Contact form (any partner) → Sales & Purchase page → new "SSB" group
     → Practice No. and KV Number.
   - Settings → Sales → new "Sprechstundenbedarf (SSB)" block → the gate
     toggle.
   - Sales order form → near the customer fields → "Contains SSB Items"
     and the SSB status (only shown once the order has an SSB item); a
     separate "SSB Prescription" group (file upload, confirmed-by,
     received-on) appears once `x_has_ssb` is true; the header gets a
     "Confirm prescription received" button once the order is `waiting`
     (visible only to `healthymed_ssb.group_ssb_prescription_officer`).
   - Sales orders list view → optional column "Contains SSB Items"
     (hidden by default - enable via the column-picker icon).
2. **Who can confirm receipt:** add a user to the
   `healthymed_ssb.group_ssb_prescription_officer` group (Settings →
   Users, under its own "HealthyMed SSB" / "SSB-Rezept-Gate" section) -
   it's a dedicated group, not a standard Odoo one (see `docs/decisions.md`
   for why).
3. **3-minute manual check:**
   - Flag any product as SSB (tick the checkbox on its form).
   - Settings → Sales → turn the SSB gate **on**.
   - Create a sales order for a customer with practice data, add the SSB
     product, confirm the order - it should show "Contains SSB Items" and
     status "Warte auf Rezept" (waiting).
   - Try to validate its delivery (Inventory) - it should be **blocked**
     with a message naming the order.
   - Back on the order, click "Confirm prescription received" (you'll
     need the officer group for this button to be visible/usable).
   - Validate the delivery again - it should now **succeed**.
4. **If you turn the gate off later** while an order is still "waiting",
   that order is **not** auto-released - use the "SSB: Recover after gate
   deactivation" action (Sales orders list or form, Action menu) on it
   deliberately.

## Task 10: healthymed_base + healthymed_chargen - where to see it, manual check (2026-11-18)

1. **Where to see each field:**
   - Product form → new "HealthyMed" notebook page → EAN, Magento ID,
     Manufacturer, Packaging Unit, Quantity Unit.
   - Contact form → Sales & Purchase page → "Sales" group (next to the
     salesperson field) → "Regional Customer (Self-Delivery)" checkbox.
   - Sales order form → next to the delivery address field → "Regional
     Self-Delivery Order" (read-only, follows the customer's flag).
   - Company form (Settings → Users & Companies → Companies) → new
     "HealthyMed" page → the two warehouse fields (not yet assigned to
     real warehouses - Task 6 never finished, see `docs/decisions.md`).
   - Lot tracking itself: Inventory → Products → a product → Inventory
     tab → Tracking = "By Lots"; Expiration Dates tab (needs the
     "Expiration Dates" feature, already on) → Shelf Life / Best Before
     / Removal / Alert Time.
2. **3-minute manual check (do this yourself):**
   - Pick (or create) a test product, set Tracking = "By Lots" and turn on
     its expiration date fields (a few days' shelf life is enough to see
     a real date).
   - Receive it into stock with a lot number and an expiry date (Inventory
     → Receipts → New, or adjust on-hand quantity with a lot).
   - Deliver it to a test customer (Sales → New order → confirm → go to
     the delivery → validate, picking/confirming the lot).
   - Print the delivery slip (Delivery → Print) and confirm the lot
     number (and expiry date, if your layout shows it) appears.
   - **Who needs to see it:** the lot number column on the slip needs
     `stock.group_lot_on_delivery_slip`; the expiry-date column
     additionally needs `product_expiry.group_expiry_date_on_delivery_slip`
     (currently off for everyone - nobody will see dates on the printed
     slip until this is turned on for a role). Both are already implied
     by the "Lager und Versand" role from Task 8 for the lot column; the
     expiry-date column isn't on for any role yet.
3. **`healthymed_chargen` needed nothing but its manifest** - standard
   Odoo (`product.template.tracking` + `product_expiry`) already covers
   everything scope 3.3 asks for. No fields, views or settings were added
   by this module.
