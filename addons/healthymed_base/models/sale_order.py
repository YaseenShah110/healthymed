from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    x_is_regional_order = fields.Boolean(
        string="Regional Self-Delivery Order",
        related="partner_id.x_is_regional",
        readonly=True,
    )
