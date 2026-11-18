# Manifest keys verified against C:\odoo\odoo19\addons\product_expiry\__manifest__.py
# Deliberately empty of models/views/data: standard Odoo price lists
# (product.pricelist / product.pricelist.item) already provide everything the
# scope (3.2, 3.3) needs. The actual price lists/rules are client data, loaded
# by scripts/bootstrap/70_pricelists.py from config/pricelists.json, not shipped
# as module XML - this module exists only to declare the dependency pairing.
# website_sale is NOT a dependency: it's already installed project-wide, and
# only the bootstrap script (not this module's own code) ever touches its
# "selectable" field.
{
    "name": "HealthyMed Pricing",
    "version": "19.0.1.0.0",
    "category": "HealthyMed",
    "summary": "Customer-status and order-volume pricing via standard Odoo price lists",
    "author": "eBakery",
    "license": "LGPL-3",
    "depends": ["healthymed_base", "sale_management"],
    "application": False,
    "installable": True,
}
