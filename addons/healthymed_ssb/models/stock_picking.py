from odoo import models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        for picking in self:
            sale_order = picking.sale_id
            if (
                picking.picking_type_id.code == "outgoing"
                and sale_order
                and sale_order.x_ssb_prescription_state == "waiting"
            ):
                raise UserError(self.env._(
                    "This delivery is linked to sale order %(order)s, which is "
                    "waiting for its SSB prescription to be confirmed. Confirm "
                    "the prescription on the order first.",
                    order=sale_order.name,
                ))
        return super().button_validate()
