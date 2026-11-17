# Manual, one-shot check (not a bootstrap script, not an automated test): creates a
# throwaway customer + product + invoice using the company's default sale tax, posts
# it, prints the result, then cleans up. All records carry ref/default_code =
# "TASK4-CHECK" so a second run can find and clean up any leftovers from a crashed
# previous run instead of colliding with them.
#
# Note: once a journal entry is posted, Odoo permanently blocks unlink() on it (and on
# anything an FK still points at from it) to protect the audit trail - `posted_before`
# stays True even after cancelling. So the invoice is cancelled (not deleted, as the
# task explicitly allows), and the product/partner it references are archived
# (active=False) rather than deleted, since deleting them is blocked by that same FK.
from odoo.fields import Command

REF = "TASK4-CHECK"

company = env["res.company"].search([], limit=1)

# Clean up any leftovers from a previous run that didn't finish.
old_moves = env["account.move"].search([("ref", "=", REF)])
still_posted = old_moves.filtered(lambda m: m.state == "posted")
if still_posted:
    still_posted.button_cancel()
old_moves.filtered(lambda m: m.state == "draft").unlink()
env["product.product"].with_context(active_test=False).search([("default_code", "=", REF)]).write({"active": False})
env["res.partner"].with_context(active_test=False).search([("ref", "=", REF)]).write({"active": False})

sale_tax = company.account_sale_tax_id
if not sale_tax:
    raise RuntimeError("Company has no default sale tax (account_sale_tax_id) set.")

partner = env["res.partner"].create({"name": "TASK4-CHECK Customer", "ref": REF})
product = env["product.product"].create({
    "name": "TASK4-CHECK Service",
    "default_code": REF,
    "type": "service",
    "list_price": 100.0,
    "taxes_id": [Command.set([sale_tax.id])],
})

move = env["account.move"].create({
    "move_type": "out_invoice",
    "partner_id": partner.id,
    "ref": REF,
    "invoice_line_ids": [Command.create({
        "product_id": product.id,
        "quantity": 1,
        "price_unit": 100.0,
        "tax_ids": [Command.set([sale_tax.id])],
    })],
})
move.action_post()

revenue_line = move.invoice_line_ids[0]
tax_lines = move.line_ids.filtered(lambda line: line.tax_line_id)

print("Untaxed amount:", move.amount_untaxed)
print("Tax amount:", move.amount_tax)
print("Total:", move.amount_total)
print("Tax rate applied:", sale_tax.amount, f"({sale_tax.name})")
print("Revenue account:", revenue_line.account_id.code, revenue_line.account_id.name)
if tax_lines:
    print("Tax account:", tax_lines[0].account_id.code, tax_lines[0].account_id.name)
else:
    print("Tax account: no tax line found")

# Clean up - cancel the move and archive the product/partner it references (none of
# the three can be unlinked now that the move has been posted; see note above).
move.button_cancel()
product.active = False
partner.active = False
print(
    f"Cleaned up test records (ref={REF}); invoice {move.name!r} left cancelled and "
    "the product/partner left archived - Odoo does not allow deleting them once the "
    "move has been posted."
)
