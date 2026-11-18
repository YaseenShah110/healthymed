from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    x_is_regional = fields.Boolean(string="Regional Customer (Self-Delivery)")
