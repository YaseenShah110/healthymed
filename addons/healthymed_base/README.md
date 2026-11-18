# healthymed_base

## Purpose

Core HealthyMed custom fields: product identifiers used for supplier/Magento
matching, the regional-customer flag, and the two warehouse roles on the
company (regional self-delivery vs. supplier/dropship handling).

## Fields

| Model | Field | Type | Label (DE) |
|---|---|---|---|
| `product.template` | `x_ean` | Char | EAN |
| `product.template` | `x_magento_id` | Char | Magento ID |
| `product.template` | `x_manufacturer` | Char | Hersteller |
| `product.template` | `x_packaging_unit` | Char | Verpackungseinheit |
| `product.template` | `x_qty_unit` | Char | Mengeneinheit |
| `res.partner` | `x_is_regional` | Boolean | Regionalkunde (Eigenbelieferung) |
| `sale.order` | `x_is_regional_order` | Boolean (related to `partner_id.x_is_regional`, readonly) | Regionale Eigenbelieferung |
| `res.company` | `x_regional_warehouse_id` | Many2one (`stock.warehouse`, `check_company=True`) | Lager für Eigenbelieferung |
| `res.company` | `x_supplier_warehouse_id` | Many2one (`stock.warehouse`, `check_company=True`) | Lager für Lieferantenabwicklung |

`x_is_regional_order` relates to `partner_id` (the order's main customer),
not `partner_shipping_id` - confirmed by the user. `x_ean`/`x_magento_id`
have no `copy`/index extras - plain fields, as specified.

## Dependencies

`product`, `sale_management`, `stock`.

## How the company warehouses are assigned

**Not yet wired.** Task 6 (which creates the two warehouses and their
stable external IDs) was never finished - `config/warehouses.json` and the
warehouses themselves don't exist yet. The bootstrap script
(`scripts/bootstrap/65_company_warehouses.py`), which should read that
config and set `x_regional_warehouse_id`/`x_supplier_warehouse_id` on the
company from it, has not been written for the same reason - writing it now
would mean guessing at external IDs that don't exist. Once Task 6 lands,
that script becomes a short, standard "look up two warehouses by stable
external ID, write if different" script, following the same pattern as
every other `scripts/bootstrap/*.py` file in this repo.

## Extending it later

Add new fields to the relevant model file in `models/`, the matching view
field in `views/`, and the label to `i18n/de.po`. The product/company
HealthyMed pages and the partner's "Sales" group are the places new
HealthyMed-specific fields on those models should go, to keep them out of
core's own groups/pages.
