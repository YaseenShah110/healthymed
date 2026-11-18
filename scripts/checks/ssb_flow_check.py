# Behaviour check (not a test): runs the full SSB flow, then rolls back everything
# it did - explicitly, via env.cr.rollback() in a finally block, not just relying on
# odoo-bin shell's own rollback-on-exit (defense in depth, same reasoning as
# invoice_check.py). All records are prefixed TASK9-CHECK.
from odoo.fields import Command

REF = "TASK9-CHECK"

company = env["res.company"].search([], limit=1)

try:
    customer = env["res.partner"].create({"name": f"{REF} Customer", "ref": REF})
    ssb_product = env["product.product"].create({
        "name": f"{REF} SSB Product",
        "default_code": REF,
        "type": "consu",
        "is_storable": True,  # type='consu' alone isn't stock-tracked; quants need this too
        "x_is_ssb": True,
        "list_price": 10.0,
    })
    normal_product = env["product.product"].create({
        "name": f"{REF} Normal Product",
        "default_code": REF,
        "type": "consu",
        "is_storable": True,
        "list_price": 5.0,
    })

    warehouse = env["stock.warehouse"].search([("company_id", "=", company.id)], limit=1)
    stock_location = warehouse.lot_stock_id
    env["stock.quant"]._update_available_quantity(ssb_product, stock_location, 10)
    env["stock.quant"]._update_available_quantity(normal_product, stock_location, 10)
    print(
        f"Gave 10 units on hand of each test product at {stock_location.complete_name!r} "
        "- needed because button_validate() on a 'consu' product delivery requires "
        "available quantity to fully validate without a backorder/negative-stock issue."
    )

    # --- Gate on, order with both an SSB and a normal item ---
    company.x_ssb_gate_enabled = True
    order1 = env["sale.order"].create({
        "partner_id": customer.id,
        "client_order_ref": REF,
        "order_line": [
            Command.create({"product_id": ssb_product.id, "product_uom_qty": 1}),
            Command.create({"product_id": normal_product.id, "product_uom_qty": 1}),
        ],
    })
    order1.action_confirm()
    print(f"\nOrder1 (gate on, has SSB): x_has_ssb={order1.x_has_ssb} state={order1.x_ssb_prescription_state!r}")

    delivery1 = order1.picking_ids.filtered(lambda p: p.picking_type_id.code == "outgoing")
    try:
        delivery1.button_validate()
        print("UNEXPECTED: delivery validated without being blocked!")
    except Exception as exc:  # noqa: BLE001 - we want to show the exact user-facing message
        print("Validation blocked as expected. Message:", str(exc))

    # Temporarily grant the current (admin) user the officer group - rolled back anyway.
    officer_group = env.ref("healthymed_ssb.group_ssb_prescription_officer")
    env.user.write({"group_ids": [Command.link(officer_group.id)]})
    order1.action_ssb_prescription_received()
    print(
        f"After 'Confirm prescription received': state={order1.x_ssb_prescription_state!r} "
        f"received_by={order1.x_ssb_prescription_received_by.name!r} "
        f"received_date={order1.x_ssb_prescription_received_date}"
    )

    delivery1.button_validate()
    print("Delivery re-validated successfully after prescription confirmed. picking state:", delivery1.state)

    # --- Gate off, a second order ---
    company.x_ssb_gate_enabled = False
    order2 = env["sale.order"].create({
        "partner_id": customer.id,
        "client_order_ref": REF,
        "order_line": [Command.create({"product_id": ssb_product.id, "product_uom_qty": 1})],
    })
    order2.action_confirm()
    print(f"\nOrder2 (gate off, has SSB): x_has_ssb={order2.x_has_ssb} state={order2.x_ssb_prescription_state!r}")

    delivery2 = order2.picking_ids.filtered(lambda p: p.picking_type_id.code == "outgoing")
    delivery2.button_validate()
    print("Order2 delivery validated without any block, as expected (gate off). picking state:", delivery2.state)

finally:
    env.cr.rollback()
    print("\nRolled back. Checking for leftovers...")
    leftover_partners = env["res.partner"].search_count([("ref", "=", REF)])
    leftover_products = env["product.product"].search_count([("default_code", "=", REF)])
    leftover_orders = env["sale.order"].search_count([("client_order_ref", "=", REF)])
    print(
        f"Leftover TASK9-CHECK records: partners={leftover_partners} "
        f"products={leftover_products} orders={leftover_orders}"
    )
