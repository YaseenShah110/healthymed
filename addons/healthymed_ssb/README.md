# healthymed_ssb

## Purpose

Marks consultation-supply (SSB - Sprechstundenbedarf) products, and
optionally blocks delivery of SSB orders until the paper prescription is
confirmed received. Does **not** depend on `healthymed_base` or
`healthymed_rollen` - its views/groups are entirely its own.

## Fields

| Model | Field | Type | Label (DE) |
|---|---|---|---|
| `product.template` | `x_is_ssb` | Boolean | Sprechstundenbedarf (SSB) |
| `product.template` | `x_pzn` | Char | PZN |
| `res.partner` | `x_praxis_nr` | Char | Praxis-Nr. (SSB) |
| `res.partner` | `x_kv_nummer` | Char | KV-Nummer |
| `res.company` | `x_ssb_gate_enabled` | Boolean | SSB-Rezept-Gate aktiv |
| `res.config.settings` | `x_ssb_gate_enabled` | Boolean (related) | SSB-Rezept-Fulfillment-Gate |
| `sale.order` | `x_has_ssb` | Boolean (computed, stored) | Enthält SSB-Artikel |
| `sale.order` | `x_ssb_prescription_file` | Binary | Rezept-Scan (optional) |
| `sale.order` | `x_ssb_prescription_filename` | Char | Rezept-Dateiname |
| `sale.order` | `x_ssb_prescription_received_by` | Many2one (res.users, readonly) | Rezept bestätigt von |
| `sale.order` | `x_ssb_prescription_received_date` | Datetime (readonly) | Rezepteingang am |
| `sale.order` | `x_ssb_prescription_state` | Selection (readonly logic) | SSB-Rezeptstatus |

## The gate

- **On confirmation** of an order (`action_confirm`): if the company gate
  (`x_ssb_gate_enabled`) is on and the order contains at least one SSB
  product (`x_has_ssb`), the state becomes `waiting`; otherwise
  `not_required`.
- **Delivery block**: `stock.picking.button_validate()` is extended -
  validating an **outgoing** delivery linked to an order still in `waiting`
  raises a clear error naming the order. Returns, internal transfers and
  deliveries of other orders are never affected.
- **"Confirm prescription received"** button (visible only in `waiting`):
  sets the state to `received`, stamps `x_ssb_prescription_received_by`/
  `_date`, and posts a chatter note. Only users in
  `healthymed_ssb.group_ssb_prescription_officer` may use it - checked in
  Python, not just hidden in the UI.
- **Turning the gate off does not change existing orders.** An order stuck
  in `waiting` stays there until someone runs the **"SSB: Recover after
  gate deactivation"** action on it (same group), which moves it to
  `not_required`. This is deliberate - toggling the gate must never
  silently release a real pending prescription requirement.
- Cancelling or resetting an order to draft does **not** reset
  `x_ssb_prescription_state` - it keeps its history. Re-confirming
  recomputes it the same way as the first confirmation.
- Duplicating an order starts a new draft, so its SSB state starts at the
  default (`not_required`) until that new order is itself confirmed.

## Who can press the button

`healthymed_ssb.group_ssb_prescription_officer` - a dedicated group under
its own category ("HealthyMed SSB") and privilege ("SSB-Rezept-Gate"), not
a standard Odoo group. This matches the senior's system, which uses the
same dedicated-group pattern elsewhere (e.g. the Megro regional-forward
release button).

## Dependencies

`product`, `sale_management`, `sale_stock` - `sale_stock` specifically for
`stock.picking.sale_id`, the link the delivery block relies on.

## Extending it later

- New SSB-relevant fields: add to the relevant model file in `models/`,
  add the view field in `views/`, add the label to `i18n/de.po`.
- Changing who can confirm receipt: edit
  `security/healthymed_ssb_security.xml`'s
  `group_ssb_prescription_officer` record (or its `implied_ids` if it
  should ever imply a standard group).
- LANR, BSNR and KV-region logic belong to a later module (Task 14), not
  here.
