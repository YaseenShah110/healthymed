from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    x_ssb_gate_enabled = fields.Boolean(string="SSB Prescription Gate Active")
