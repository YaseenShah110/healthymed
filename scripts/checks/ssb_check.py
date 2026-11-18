# Read-only structure check (not a test): for every field healthymed_ssb's spec
# requires, confirms it exists on the right model with the right type and the
# right German label (read via fields_get with lang=de_DE, the standard
# introspection API, so it reflects what the UI actually shows). Changes nothing.
EXPECTED = [
    ("product.template", "x_is_ssb", "boolean", "Sprechstundenbedarf (SSB)"),
    ("product.template", "x_pzn", "char", "PZN"),
    ("res.partner", "x_praxis_nr", "char", "Praxis-Nr. (SSB)"),
    ("res.partner", "x_kv_nummer", "char", "KV-Nummer"),
    ("res.company", "x_ssb_gate_enabled", "boolean", "SSB-Rezept-Gate aktiv"),
    ("res.config.settings", "x_ssb_gate_enabled", "boolean", "SSB-Rezept-Fulfillment-Gate"),
    ("sale.order", "x_has_ssb", "boolean", "Enthält SSB-Artikel"),
    ("sale.order", "x_ssb_prescription_file", "binary", "Rezept-Scan (optional)"),
    ("sale.order", "x_ssb_prescription_filename", "char", "Rezept-Dateiname"),
    ("sale.order", "x_ssb_prescription_received_by", "many2one", "Rezept bestätigt von"),
    ("sale.order", "x_ssb_prescription_received_date", "datetime", "Rezepteingang am"),
    ("sale.order", "x_ssb_prescription_state", "selection", "SSB-Rezeptstatus"),
]

EXPECTED_SELECTION = {
    "not_required": "Nicht erforderlich",
    "waiting": "Warte auf Rezept",
    "received": "Rezept eingegangen",
}

header = f"{'Model':<22} {'Field':<32} {'Type OK':<8} {'Label OK':<9} Notes"
print(header)
print("-" * len(header))

for model, field_name, expected_type, expected_label in EXPECTED:
    fields_de = env[model].with_context(lang="de_DE").fields_get([field_name])
    notes = []
    if field_name not in fields_de:
        print(f"{model:<22} {field_name:<32} {'MISSING':<8} {'MISSING':<9} field does not exist")
        continue

    info = fields_de[field_name]
    type_ok = info["type"] == expected_type
    label_ok = info["string"] == expected_label
    if not type_ok:
        notes.append(f"type={info['type']!r} expected {expected_type!r}")
    if not label_ok:
        notes.append(f"label={info['string']!r} expected {expected_label!r}")

    if field_name == "x_has_ssb":
        stored = env[model]._fields[field_name].store
        notes.append(f"stored={stored}")
        if not stored:
            notes.append("EXPECTED stored=True")

    if field_name == "x_ssb_prescription_state":
        actual_selection = dict(info.get("selection") or [])
        if actual_selection != EXPECTED_SELECTION:
            notes.append(f"selection={actual_selection!r} expected {EXPECTED_SELECTION!r}")
        else:
            notes.append(f"selection OK: {actual_selection}")

    print(f"{model:<22} {field_name:<32} {str(type_ok):<8} {str(label_ok):<9} {'; '.join(notes)}")
