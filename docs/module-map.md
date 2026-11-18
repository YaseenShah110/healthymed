# Module map

**Eight modules in the active build order** (down from nine -
`healthymed_megro_import` deferred by team decision, 2026-11-18 - see
`docs/decisions.md`), plus two deferred modules. Dependencies below were
checked against each **already-built** module's real `__manifest__.py` (not
memory) - one real difference was found, noted under module 8 (theme).

**Products come only from a sample export of the senior's system (~100
items); no supplier import is built.**

| # | Module | Depends | Contents (one line) | Status |
|---|---|---|---|---|
| 1 | `healthymed_base` | `product`, `sale_management`, `stock` | Core custom fields: EAN/Magento ID/manufacturer/packaging/qty unit on products, regional-customer flag on partners, regional-order flag on sale orders, the two warehouse fields on the company | **built** (Task 10) - real manifest matches this list exactly |
| 2 | `healthymed_rollen` | `sales_team`, `stock`, `account`, `purchase`, `website` | HealthyMed roles (Innendienst, Lager und Versand, Buchhaltung, Geschäftsführung) built only by implying standard groups | **built** - real manifest matches this list exactly |
| 3 | `healthymed_ssb` | `product`, `sale_management`, `sale_stock` | SSB marking on products, practice data on partners, the SSB prescription gate and delivery block on sale orders | **built** - real manifest matches this list exactly |
| 4 | `healthymed_chargen` | `healthymed_base`, `product_expiry` | Manifest-only - standard Odoo (`tracking` + `product_expiry`) already covers scope 3.3's batch/best-before requirement | **built** (Task 10) - real manifest matches this list exactly |
| 5 | `healthymed_pricing` | `healthymed_base`, `sale_management` | Customer-specific price lists (not yet specified to this session beyond this line) | **pending** |
| 6 | `healthymed_shop` | `healthymed_base`, `website_sale`, `delivery` | Online shop functional wiring (not yet specified to this session beyond this line) | **pending** |
| 7 | `healthymed_rezept_kv` | `healthymed_ssb` | LANR/BSNR/KV-region logic (not yet specified to this session beyond this line) | **pending** |
| 8 | `healthymed_theme` | ~~`healthymed_base`, `healthymed_ssb`, `healthymed_shop`, `website_sale`~~ **real: `website`, `website_sale`** | Figma-approved visual theme (layout/topbar/header, SCSS variable overrides, Builder-editable snippets) - no custom fields, no models | **built** - already exists in `addons/`, already installed; built by a parallel session, not this task chain. **Dependency correction:** the real `__manifest__.py` depends on `website`+`website_sale` only - it does not depend on any `healthymed_*` module at all, consistent with it being a pure visual layer with zero custom-field logic. |

**Deferred by team decision (2026-11-18): `healthymed_megro_import`.**
`depends` would have been `healthymed_base`, `purchase`. Its three custom
models (`healthymed.megro.feed`, `healthymed.megro.feed.column`,
`healthymed.megro.import.log`) and "the four product fields" it would have
added are named in this task's own brief but their actual field
names/types/labels were never specified to this session - not guessed (see
`docs/field-spec.json`). No feed, no MeGro-specific fields; vendor
name/code use standard Odoo fields instead.

**Deferred by team decision: `healthymed_megro_dropship`** (date/reason in
`docs/decisions.md`). Fields `x_megro_sent_by`, `x_megro_sent_on`,
`x_regional_forward_ok`, `x_regional_forward_by`, `x_regional_forward_on`,
plus "the two order config models" - names only, no types/models/labels ever
specified to this session; not guessed (see `docs/field-spec.json`).

**Superseded by the deferral above:** the previous "open decision" here
about `healthymed_megro_import` possibly matching supplier data by
`x_pzn` via a runtime check no longer applies - there is no import module
to make that decision in.
