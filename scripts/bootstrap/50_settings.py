# Applies the approved settings from config/settings.json through the same mechanism
# the Settings UI uses: create a res.config.settings record (which defaults every
# field to its real current value), override only the approved fields, then call
# execute() - never overridden in Odoo itself except via set_values(), see
# C:\odoo\odoo19\odoo\addons\base\models\res_config.py.
import json
import os

repo_root = os.environ["REPO_ROOT"]
config_path = os.path.join(repo_root, "config", "settings.json")
if not os.path.isfile(config_path):
    raise FileNotFoundError(f"Missing required config file: {config_path}")

with open(config_path, encoding="utf-8") as f:
    entries = json.load(f)

Settings = env["res.config.settings"]

# Fail loudly before changing anything if a model/field doesn't exist.
for entry in entries:
    if entry["model"] != "res.config.settings":
        raise RuntimeError(
            f"Unsupported model in {config_path}: {entry['model']!r} "
            "(only res.config.settings is supported by this script)"
        )
    if entry["field"] not in Settings._fields:
        raise RuntimeError(f"Field {entry['field']!r} does not exist on res.config.settings in this Odoo install.")

current = Settings.create({})
diff = {entry["field"]: entry["value"] for entry in entries if getattr(current, entry["field"]) != entry["value"]}

if diff:
    current.write(diff)
    current.execute()
    env.cr.commit()
    after = Settings.create({})
    changed = {field: getattr(after, field) for field in diff}
    print("Changed:", changed)
else:
    print("no changes")
