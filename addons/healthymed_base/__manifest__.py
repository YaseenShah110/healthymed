# Manifest keys verified against C:\odoo\odoo19\addons\product_expiry\__manifest__.py
{
    "name": "HealthyMed Base",
    "version": "19.0.1.0.0",
    "category": "HealthyMed",
    "summary": "Core HealthyMed fields: product identifiers, regional customers, warehouse roles",
    "author": "eBakery",
    "license": "LGPL-3",
    "depends": ["product", "sale_management", "stock"],
    "data": [
        "views/product_template_views.xml",
        "views/res_partner_views.xml",
        "views/sale_order_views.xml",
        "views/res_company_views.xml",
    ],
    "application": False,
    "installable": True,
}
