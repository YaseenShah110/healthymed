from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    x_ssb_gate_enabled = fields.Boolean(
        related="company_id.x_ssb_gate_enabled",
        readonly=False,
        string="SSB Prescription Fulfillment Gate",
    )
