# Manifest keys verified against C:\odoo\odoo19\addons\product_expiry\__manifest__.py
{
    "name": "HealthyMed SSB",
    "version": "19.0.1.0.0",
    "category": "HealthyMed",
    "summary": "SSB (Sprechstundenbedarf) marking and prescription gate",
    "author": "eBakery",
    "license": "LGPL-3",
    "depends": ["product", "sale_management", "sale_stock"],
    "data": [
        "security/healthymed_ssb_security.xml",
        "views/product_template_views.xml",
        "views/res_partner_views.xml",
        "views/sale_order_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "application": False,
    "installable": True,
}
