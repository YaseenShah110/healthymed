# Manifest keys verified against C:\odoo\odoo19\addons\product_expiry\__manifest__.py
{
    "name": "HealthyMed Roles",
    "version": "19.0.1.0.0",
    "category": "HealthyMed",
    "summary": "HealthyMed roles built only from standard Odoo access groups",
    "author": "eBakery",
    "license": "LGPL-3",
    "depends": ["sales_team", "stock", "account", "purchase", "website"],
    "data": [
        "security/healthymed_rollen_groups.xml",
    ],
    "application": False,
    "installable": True,
}
