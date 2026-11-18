# Module map

Nine modules, in build order, plus one deferred module. Dependencies below
were checked against each **already-built** module's real `__manifest__.py`
(not memory) - one real difference was found, noted under module 9.

| # | Module | Depends | Contents (one line) | Status |
|---|---|---|---|---|
| 1 | `healthymed_base` | `product`, `sale_management`, `stock` | Core custom fields: EAN/Magento ID/manufacturer/packaging/qty unit on products, regional-customer flag on partners, regional-order flag on sale orders, the two warehouse fields on the company | **pending** - never built (Task 7 stalled waiting on step-2 answers; work moved to Tasks 8/9 instead) |
| 2 | `healthymed_rollen` | `sales_team`, `stock`, `account`, `purchase`, `website` | HealthyMed roles (Innendienst, Lager und Versand, Buchhaltung, Geschäftsführung) built only by implying standard groups | **built** - real manifest matches this list exactly |
| 3 | `healthymed_ssb` | `product`, `sale_management`, `sale_stock` | SSB marking on products, practice data on partners, the SSB prescription gate and delivery block on sale orders | **built** - real manifest matches this list exactly |
| 4 | `healthymed_chargen` | `healthymed_base`, `product_expiry` | Batch/best-before fields and processes (not yet specified to this session beyond this line) | **pending** |
| 5 | `healthymed_megro_import` | `healthymed_base`, `purchase` | MeGro supplier product/price/availability import (not yet specified to this session beyond this line) | **pending** |
| 6 | `healthymed_pricing` | `healthymed_base`, `sale_management` | Customer-specific price lists (not yet specified to this session beyond this line) | **pending** |
| 7 | `healthymed_shop` | `healthymed_base`, `website_sale`, `delivery` | Online shop functional wiring (not yet specified to this session beyond this line) | **pending** |
| 8 | `healthymed_rezept_kv` | `healthymed_ssb` | LANR/BSNR/KV-region logic (not yet specified to this session beyond this line) | **pending** |
| 9 | `healthymed_theme` | ~~`healthymed_base`, `healthymed_ssb`, `healthymed_shop`, `website_sale`~~ **real: `website`, `website_sale`** | Figma-approved visual theme (layout/topbar/header, SCSS variable overrides, Builder-editable snippets) - no custom fields, no models | **built** - already exists in `addons/`, already installed; built by a parallel session, not this task chain. **Dependency correction:** the real `__manifest__.py` depends on `website`+`website_sale` only - it does not depend on any `healthymed_*` module at all, consistent with it being a pure visual layer with zero custom-field logic. |

**Deferred:** `healthymed_megro_dropship` (team decision - see `docs/decisions.md`
for date/reason). Fields `x_megro_sent_by`, `x_megro_sent_on`,
`x_regional_forward_ok`, `x_regional_forward_by`, `x_regional_forward_on`,
plus "the two order config models" - names only, no types/models/labels ever
specified to this session; not guessed (see `docs/field-spec.json`).

**Open decision on `healthymed_megro_import`:** it may match supplier data by
`x_pzn` - but that field lives in `healthymed_ssb`, not in `healthymed_base`
or `megro_import` itself. The plan is a **runtime check** (verify `x_pzn`
exists on the model before using it) rather than a hard module dependency on
`healthymed_ssb`, so `megro_import` doesn't have to depend on a module whose
field it only optionally uses.
