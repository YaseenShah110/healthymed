# Creates/updates payment terms from config/payment_terms.json, matched by a stable
# external ID built from each entry's "key" (not by name), using Odoo's own data-free
# upsert mechanism: Model._load_records([{xml_id, values, noupdate}], update=True)
# (see C:\odoo\odoo19\odoo\orm\models.py - this is what XML/CSV data loading itself
# calls internally; there is no ir.model.data._update() method in Odoo 19).
import json
import os

from odoo.fields import Command
from odoo.tools import html2plaintext

repo_root = os.environ["REPO_ROOT"]
config_path = os.path.join(repo_root, "config", "payment_terms.json")
if not os.path.isfile(config_path):
    raise FileNotFoundError(f"Missing required config file: {config_path}")

with open(config_path, encoding="utf-8") as f:
    terms_cfg = json.load(f)

MODULE = "healthymed"
PaymentTerm = env["account.payment.term"]
ImdSudo = env["ir.model.data"].sudo()


# account.payment.term.line.days_next_month defaults to '10' regardless of delay_type
# (it's only hidden in the UI for other delay types, not actually blank in the DB) -
# match that default when a line's config doesn't specify it, or every such line would
# look "changed" forever even when nothing differs.
DAYS_NEXT_MONTH_DEFAULT = "10"


def line_tuple(line):
    return (
        line["value"],
        round(float(line["value_amount"]), 4),
        line["delay_type"],
        int(line.get("nb_days", 0)),
        line.get("days_next_month") or DAYS_NEXT_MONTH_DEFAULT,
    )


def existing_line_tuple(line_record):
    return (
        line_record.value,
        round(line_record.value_amount, 4),
        line_record.delay_type,
        line_record.nb_days,
        line_record.days_next_month or DAYS_NEXT_MONTH_DEFAULT,
    )


changed_keys = []
data_list = []

for entry in terms_cfg:
    xml_id = f"{MODULE}.payment_term_{entry['key']}"
    existing_imd = ImdSudo.search(
        [
            ("module", "=", MODULE),
            ("name", "=", f"payment_term_{entry['key']}"),
            ("model", "=", "account.payment.term"),
        ],
        limit=1,
    )
    existing = PaymentTerm.browse(existing_imd.res_id) if existing_imd else PaymentTerm.browse()

    desired_lines = [line_tuple(line) for line in entry["lines"]]
    note_value = entry.get("note") or ""

    needs_write = True
    if existing:
        current_lines = [existing_line_tuple(line_record) for line_record in existing.line_ids]
        current_note = html2plaintext(existing.note or "").strip()
        needs_write = (
            existing.name != entry["name"]
            or current_note != note_value.strip()
            or current_lines != desired_lines
        )

    if needs_write:
        values = {
            "name": entry["name"],
            "note": note_value or False,
            "line_ids": [Command.clear()] + [
                Command.create({
                    "value": line["value"],
                    "value_amount": line["value_amount"],
                    "delay_type": line["delay_type"],
                    "nb_days": line.get("nb_days", 0),
                    **({"days_next_month": line["days_next_month"]} if "days_next_month" in line else {}),
                })
                for line in entry["lines"]
            ],
        }
        data_list.append({"xml_id": xml_id, "values": values, "noupdate": False})
        changed_keys.append(entry["key"])

if data_list:
    PaymentTerm._load_records(data_list, update=True)
    env.cr.commit()
    print("Changed:", changed_keys)
else:
    print("no changes")
