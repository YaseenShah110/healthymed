from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    x_praxis_nr = fields.Char(string="Practice No. (SSB)")
    x_kv_nummer = fields.Char(string="KV Number")
