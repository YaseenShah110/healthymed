# Sets the main company's identity, address, language and timezone from
# config/company.json. Writes only the fields listed below; nothing about the
# chart of accounts, taxes, journals or any other company field is touched here.
#
# Note: "legal_name" has no corresponding Odoo 19 field on res.company/res.partner
# (verified against base, account, l10n_de - none add one). It is required in the
# config file for documentation purposes only and is never written to Odoo.
import base64
import json
import os

REQUIRED_KEYS = [
    "name", "legal_name", "street", "street2", "zip", "city",
    "country_code", "currency_code", "vat", "email", "phone", "website",
    "default_language_code", "timezone", "logo_path",
]

repo_root = os.environ["REPO_ROOT"]
config_path = os.path.join(repo_root, "config", "company.json")
if not os.path.isfile(config_path):
    raise FileNotFoundError(f"Missing required config file: {config_path}")

with open(config_path, encoding="utf-8") as f:
    cfg = json.load(f)

missing = [k for k in REQUIRED_KEYS if k not in cfg]
if missing:
    raise RuntimeError(f"Missing required key(s) in {config_path}: {missing}")

company = env["res.company"].search([], limit=1)
if not company:
    raise RuntimeError("No res.company record found.")
partner = company.partner_id

changes_summary = []

# --- country / state / currency lookups by code ---
country = env["res.country"].search([("code", "=", cfg["country_code"])], limit=1)
if not country:
    raise RuntimeError(f"No res.country found for country_code={cfg['country_code']!r}")

state_id = False
state_code = cfg.get("state_code") or None
if state_code:
    states = env["res.country.state"].search([("code", "=", state_code), ("country_id", "=", country.id)])
    if len(states) != 1:
        raise RuntimeError(
            f"Expected exactly one res.country.state for state_code={state_code!r} in "
            f"country {country.code!r}, found {len(states)}"
        )
    state_id = states.id

currency = env["res.currency"].with_context(active_test=False).search([("name", "=", cfg["currency_code"])], limit=1)
if not currency:
    raise RuntimeError(f"No res.currency found for currency_code={cfg['currency_code']!r}")
if not currency.active:
    currency.active = True
    changes_summary.append(f"activated currency {currency.name}")

# --- company fields: write only what differs ---
field_map = {
    "name": cfg["name"] or False,
    "street": cfg["street"] or False,
    "street2": cfg["street2"] or False,
    "zip": cfg["zip"] or False,
    "city": cfg["city"] or False,
    "country_id": country.id,
    "currency_id": currency.id,
    "vat": cfg["vat"] or False,
    "email": cfg["email"] or False,
    "phone": cfg["phone"] or False,
    "website": cfg["website"] or False,
    "company_registry": cfg.get("company_registry") or False,
}
if state_id:
    field_map["state_id"] = state_id

company_diff = {}
for key, value in field_map.items():
    current = getattr(company, key)
    if key.endswith("_id"):
        current = current.id if current else False
    else:
        current = current or False
    if current != value:
        company_diff[key] = value

if company_diff:
    company.write(company_diff)
    changes_summary.append(f"company fields: {sorted(company_diff.keys())}")

# --- language: activate + load translations via Odoo's own wizard, then set partner lang/tz ---
lang_code = cfg["default_language_code"]
lang = env["res.lang"].with_context(active_test=False).search([("code", "=", lang_code)], limit=1)
if not lang:
    raise RuntimeError(f"No res.lang found for default_language_code={lang_code!r}")

if not lang.active:
    installer = env["base.language.install"].create({
        "lang_ids": [(6, 0, [lang.id])],
        "overwrite": True,
    })
    installer.lang_install()
    changes_summary.append(f"installed language {lang_code} + translations for installed modules")

partner_diff = {}
if partner.lang != lang_code:
    partner_diff["lang"] = lang_code
if partner.tz != cfg["timezone"]:
    partner_diff["tz"] = cfg["timezone"]
if partner_diff:
    partner.write(partner_diff)
    changes_summary.append(f"partner fields: {sorted(partner_diff.keys())}")

# --- logo: validate, write only if it differs, skip clearly if missing ---
logo_path = cfg["logo_path"]
abs_logo_path = os.path.join(repo_root, logo_path) if logo_path else None
if not logo_path or not os.path.isfile(abs_logo_path):
    print(f"Logo: no file at {logo_path!r}, skipping.")
else:
    from PIL import Image

    with Image.open(abs_logo_path) as img:
        img.verify()
    with open(abs_logo_path, "rb") as f:
        logo_b64 = base64.b64encode(f.read())
    if company.logo != logo_b64:
        company.logo = logo_b64
        changes_summary.append(f"logo set from {logo_path}")

if changes_summary:
    env.cr.commit()
    print("Changed:", changes_summary)
else:
    print("no changes")
