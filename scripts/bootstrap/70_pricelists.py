# Creates/updates price lists and their rules from config/pricelists.json, matched by
# stable external IDs in the "healthymed_pricing" namespace (never by name or database
# ID), using the same data-free upsert mechanism as 45_payment_terms.py:
# Model._load_records([{xml_id, values, noupdate}], update=True) - see
# C:\odoo\odoo19\odoo\orm\models.py. Writes only differences. Never archives or
# deletes - this script only ever creates/updates.
import json
import os

from odoo.fields import Command

MODULE = "healthymed_pricing"

repo_root = os.environ["REPO_ROOT"]
config_path = os.path.join(repo_root, "config", "pricelists.json")
if not os.path.isfile(config_path):
    raise FileNotFoundError(f"Missing required config file: {config_path}")

with open(config_path, encoding="utf-8") as f:
    pricelists_cfg = json.load(f)

REQUIRED_LIST_KEYS = ("key", "name", "currency_code", "rules")
REQUIRED_RULE_KEYS = ("applied_on", "min_quantity", "compute_price", "value")
SUPPORTED_COMPUTE_PRICE = ("fixed", "percentage")  # "formula" not approved for this module

Pricelist = env["product.pricelist"]
ImdSudo = env["ir.model.data"].sudo()


def find_currency(code):
    currency = env["res.currency"].with_context(active_test=False).search([("name", "=", code)], limit=1)
    if not currency:
        raise RuntimeError(f"No res.currency found for currency_code={code!r}")
    if not currency.active:
        currency.active = True
    return currency


def find_category(ref):
    category = env.ref(ref, raise_if_not_found=False)
    if not category:
        raise RuntimeError(f"No product.category found for category_ref={ref!r}")
    return category


def rule_value_field(compute_price):
    if compute_price not in SUPPORTED_COMPUTE_PRICE:
        raise RuntimeError(
            f"Unsupported compute_price {compute_price!r} - only {SUPPORTED_COMPUTE_PRICE} "
            "are supported by this script (formula was not approved for this module)."
        )
    return "fixed_price" if compute_price == "fixed" else "percent_price"


def rule_tuple(rule_cfg):
    for key in REQUIRED_RULE_KEYS:
        if key not in rule_cfg:
            raise RuntimeError(f"Missing required rule key {key!r} in a rule for {config_path}")
    category_ref = rule_cfg.get("category_ref")
    categ_id = find_category(category_ref).id if category_ref else False
    return (
        rule_cfg["applied_on"],
        categ_id,
        round(float(rule_cfg["min_quantity"]), 4),
        rule_cfg["compute_price"],
        round(float(rule_cfg["value"]), 4),
        rule_cfg.get("date_start") or False,
        rule_cfg.get("date_end") or False,
    )


def existing_rule_tuple(item):
    value_field = rule_value_field(item.compute_price)
    return (
        item.applied_on,
        item.categ_id.id or False,
        round(item.min_quantity, 4),
        item.compute_price,
        round(getattr(item, value_field), 4),
        item.date_start or False,
        item.date_end or False,
    )


changed_keys = []
data_list = []

for list_cfg in pricelists_cfg:
    for key in REQUIRED_LIST_KEYS:
        if key not in list_cfg:
            raise RuntimeError(f"Missing required key {key!r} in {config_path}")

    xml_id = f"{MODULE}.pricelist_{list_cfg['key']}"
    existing_imd = ImdSudo.search(
        [
            ("module", "=", MODULE),
            ("name", "=", f"pricelist_{list_cfg['key']}"),
            ("model", "=", "product.pricelist"),
        ],
        limit=1,
    )
    existing = Pricelist.browse(existing_imd.res_id) if existing_imd else Pricelist.browse()

    currency = find_currency(list_cfg["currency_code"])
    selectable = bool(list_cfg.get("selectable_on_website", False))
    desired_rules = [rule_tuple(rule_cfg) for rule_cfg in list_cfg["rules"]]

    needs_write = True
    if existing:
        current_rules = [existing_rule_tuple(item) for item in existing.item_ids]
        needs_write = (
            existing.name != list_cfg["name"]
            or existing.currency_id.id != currency.id
            or bool(existing.selectable) != selectable
            or current_rules != desired_rules
        )

    if needs_write:
        values = {
            "name": list_cfg["name"],
            "currency_id": currency.id,
            "selectable": selectable,
            "item_ids": [Command.clear()] + [
                Command.create({
                    "applied_on": rule_cfg["applied_on"],
                    "categ_id": (find_category(rule_cfg["category_ref"]).id if rule_cfg.get("category_ref") else False),
                    "min_quantity": rule_cfg["min_quantity"],
                    "compute_price": rule_cfg["compute_price"],
                    rule_value_field(rule_cfg["compute_price"]): rule_cfg["value"],
                    "date_start": rule_cfg.get("date_start") or False,
                    "date_end": rule_cfg.get("date_end") or False,
                })
                for rule_cfg in list_cfg["rules"]
            ],
        }
        data_list.append({"xml_id": xml_id, "values": values, "noupdate": False})
        changed_keys.append(list_cfg["key"])

if data_list:
    Pricelist._load_records(data_list, update=True)
    env.cr.commit()
    print("Changed:", changed_keys)
else:
    print("no changes")
