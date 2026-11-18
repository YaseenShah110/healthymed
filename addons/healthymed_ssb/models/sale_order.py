from odoo import api, fields, models
from odoo.exceptions import UserError

SSB_STATES = [
    ("not_required", "Not required"),
    ("waiting", "Waiting for prescription"),
    ("received", "Prescription received"),
]


class SaleOrder(models.Model):
    _inherit = "sale.order"

    x_has_ssb = fields.Boolean(
        string="Contains SSB Items",
        compute="_compute_x_has_ssb",
        store=True,
    )
    x_ssb_prescription_file = fields.Binary(string="Prescription Scan (optional)")
    x_ssb_prescription_filename = fields.Char(string="Prescription Filename")
    x_ssb_prescription_received_by = fields.Many2one(
        "res.users", string="Prescription Confirmed By", readonly=True
    )
    x_ssb_prescription_received_date = fields.Datetime(
        string="Prescription Received On", readonly=True
    )
    x_ssb_prescription_state = fields.Selection(
        SSB_STATES,
        string="SSB Prescription Status",
        default="not_required",
        tracking=True,
    )

    @api.depends("order_line.product_id.x_is_ssb")
    def _compute_x_has_ssb(self):
        for order in self:
            order.x_has_ssb = any(line.product_id.x_is_ssb for line in order.order_line)

    def action_confirm(self):
        res = super().action_confirm()
        for order in self:
            if order.company_id.x_ssb_gate_enabled and order.x_has_ssb:
                order.x_ssb_prescription_state = "waiting"
            else:
                order.x_ssb_prescription_state = "not_required"
        return res

    def action_ssb_prescription_received(self):
        self.ensure_one()
        if not self.env.user.has_group("healthymed_ssb.group_ssb_prescription_officer"):
            raise UserError(self.env._("You are not allowed to confirm SSB prescriptions."))
        if self.x_ssb_prescription_state != "waiting":
            raise UserError(self.env._("This order's SSB prescription is not waiting for confirmation."))
        self.write({
            "x_ssb_prescription_state": "received",
            "x_ssb_prescription_received_by": self.env.user.id,
            "x_ssb_prescription_received_date": fields.Datetime.now(),
        })
        self.message_post(body=self.env._("SSB prescription confirmed received."))

    def action_ssb_gate_recover(self):
        """Manual recovery for orders left in 'waiting' after the SSB gate was
        switched off. Does not run automatically - the gate being off only
        affects new orders at confirmation time (action_confirm)."""
        for order in self:
            if order.x_ssb_prescription_state == "waiting" and not order.company_id.x_ssb_gate_enabled:
                order.x_ssb_prescription_state = "not_required"
                order.message_post(body=self.env._("SSB prescription requirement released: gate is off."))
