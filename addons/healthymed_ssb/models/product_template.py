from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    x_is_ssb = fields.Boolean(string="Consultation Supply (SSB)")
    x_pzn = fields.Char(string="PZN")
