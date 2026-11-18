# Manual, read-only-in-effect check (not an automated test): creates one temporary
# user per healthymed_rollen role, checks model access (has_access, the Odoo 19
# public API - see odoo/orm/models.py) and key menu visibility (ir.ui.menu.
# _visible_menu_ids(), the same method Odoo's own menu loading uses), prints a
# table, then deletes every user it created - even if something raised. Never
# touches real users. No password is set, written or printed anywhere.
PREFIX = "TASK8-CHECK"
EMAIL_DOMAIN = "example.com"  # IANA-reserved for documentation/examples (RFC 2606)

ROLE_GROUPS = {
    "Innendienst": "healthymed_rollen.group_innendienst",
    "Lager und Versand": "healthymed_rollen.group_lager_und_versand",
    "Buchhaltung": "healthymed_rollen.group_buchhaltung",
    "Geschaeftsfuehrung": "healthymed_rollen.group_geschaeftsfuehrung",
}

MODELS_TO_CHECK = ["sale.order", "stock.picking", "stock.lot", "account.move", "purchase.order"]
OPERATIONS = ("read", "create", "write", "unlink")

MENUS_TO_CHECK = {
    "Sales": "sale.sale_menu_root",
    "Inventory": "stock.menu_stock_root",
    "Accounting": "account.menu_finance",
    "Purchase": "purchase.menu_purchase_root",
    "Website": "website.menu_website_configuration",
}

SLUG_MAP = str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss", " ": "-"})

created_users = env["res.users"].browse()
rows = []

try:
    for role_name, group_xmlid in ROLE_GROUPS.items():
        group = env.ref(group_xmlid)
        slug = role_name.lower().translate(SLUG_MAP)
        login = f"{PREFIX}-{slug}@{EMAIL_DOMAIN}"

        user = env["res.users"].create({
            "name": f"{PREFIX} {role_name}",
            "login": login,
            "email": login,
            "group_ids": [(6, 0, [group.id])],
        })
        created_users |= user

        for model in MODELS_TO_CHECK:
            scoped_model = env[model].with_user(user).browse()
            for op in OPERATIONS:
                allowed = scoped_model.has_access(op)
                rows.append((role_name, model, op, "yes" if allowed else "no"))

        visible_ids = env["ir.ui.menu"].with_user(user)._visible_menu_ids()
        for menu_label, menu_xmlid in MENUS_TO_CHECK.items():
            menu = env.ref(menu_xmlid, raise_if_not_found=False)
            visible = bool(menu and menu.id in visible_ids)
            rows.append((role_name, f"menu:{menu_label}", "visible", "yes" if visible else "no"))

    header = f"{'Role':<20} {'Model / menu':<22} {'Operation':<10} Allowed"
    print(header)
    print("-" * len(header))
    for role, target, op, allowed in rows:
        print(f"{role:<20} {target:<22} {op:<10} {allowed}")
finally:
    count = len(created_users)
    created_users.unlink()
    print(f"\nDeleted {count} temporary user(s) (prefix {PREFIX!r}).")
