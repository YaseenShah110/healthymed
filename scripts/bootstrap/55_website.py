# Updates the existing website record from config/website.json - never creates a
# second one. Activates languages by code (they must already be installed, e.g. by
# Task 3's language-install step) and sets the customer account signup mode. Does not
# touch domain, SSL, analytics, social accounts, cookie texts or any SEO field.
import json
import os

repo_root = os.environ["REPO_ROOT"]
config_path = os.path.join(repo_root, "config", "website.json")
if not os.path.isfile(config_path):
    raise FileNotFoundError(f"Missing required config file: {config_path}")

with open(config_path, encoding="utf-8") as f:
    cfg = json.load(f)

for required_key in ("name", "default_language_code", "extra_language_codes", "auth_signup_uninvited"):
    if required_key not in cfg:
        raise RuntimeError(f"Missing required key {required_key!r} in {config_path}")

website = env["website"].search([], limit=1, order="id")
if not website:
    raise RuntimeError("No website record found - this script only updates an existing one.")


def find_active_lang(code):
    lang = env["res.lang"].search([("code", "=", code), ("active", "=", True)], limit=1)
    if not lang:
        raise RuntimeError(
            f"No active res.lang found for code {code!r}. Languages must already be "
            "installed/activated (see Task 3's language-install step) before this script runs."
        )
    return lang


default_lang = find_active_lang(cfg["default_language_code"])
extra_langs = env["res.lang"].browse()
for code in cfg["extra_language_codes"]:
    extra_langs |= find_active_lang(code)

desired_language_ids = (default_lang | extra_langs).ids

diff = {}
if website.name != cfg["name"]:
    diff["name"] = cfg["name"]
if website.default_lang_id.id != default_lang.id:
    diff["default_lang_id"] = default_lang.id
if set(website.language_ids.ids) != set(desired_language_ids):
    diff["language_ids"] = [(6, 0, desired_language_ids)]
if website.auth_signup_uninvited != cfg["auth_signup_uninvited"]:
    diff["auth_signup_uninvited"] = cfg["auth_signup_uninvited"]

if diff:
    website.write(diff)
    env.cr.commit()
    print("Changed:", sorted(diff.keys()))
else:
    print("no changes")
