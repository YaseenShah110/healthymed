from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    x_ean = fields.Char(string="EAN")
    x_magento_id = fields.Char(string="Magento ID")
    x_manufacturer = fields.Char(string="Manufacturer")
    x_packaging_unit = fields.Char(string="Packaging Unit")
    x_qty_unit = fields.Char(string="Quantity Unit")
