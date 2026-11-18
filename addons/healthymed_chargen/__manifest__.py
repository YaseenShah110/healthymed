# Manifest keys verified against C:\odoo\odoo19\addons\product_expiry\__manifest__.py
# Deliberately empty of models/views/data: standard Odoo (product.template.tracking +
# product_expiry) already provides everything the scope (3.3) asks for. This module
# exists only to declare that dependency pairing for HealthyMed, not to add anything.
{
    "name": "HealthyMed Batch/Expiry",
    "version": "19.0.1.0.0",
    "category": "HealthyMed",
    "summary": "Batch and best-before date handling - configuration only, no custom fields",
    "author": "eBakery",
    "license": "LGPL-3",
    "depends": ["healthymed_base", "product_expiry"],
    "application": False,
    "installable": True,
}
