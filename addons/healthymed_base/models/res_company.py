from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    x_regional_warehouse_id = fields.Many2one(
        "stock.warehouse",
        string="Warehouse for Self-Delivery",
        check_company=True,
    )
    x_supplier_warehouse_id = fields.Many2one(
        "stock.warehouse",
        string="Warehouse for Supplier Handling",
        check_company=True,
    )
