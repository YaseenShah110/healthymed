# healthymed_rollen

## Purpose

Defines HealthyMed's four roles as an access-rights privilege, built **only**
by implying existing standard Odoo 19 groups. No new models, no new
permission logic, no record rules.

## Structure

- Category: **HealthyMed** (`ir.module.category`)
- Privilege: **HealthyMed-Rolle** (`res.groups.privilege`, under that category)
- Four roles (`res.groups`, each a level of that privilege):

| Role | Implies (standard groups) |
|---|---|
| Innendienst | Sales: User - All Documents (`sales_team.group_sale_salesman_all_leads`), Inventory: User (`stock.group_stock_user`) |
| Lager und Versand | Inventory: User, Manage Lots/Serial Numbers (`stock.group_production_lot`), Show Lot on Delivery Slip (`stock.group_lot_on_delivery_slip`) |
| Buchhaltung | Sales: User - All Documents, Accounting/Invoicing (`account.group_account_invoice`) |
| Geschäftsführung | Everything in the three roles above (via implying the role groups themselves - not re-listed), plus Sales: Administrator (`sales_team.group_sale_manager`), Purchase: User (`purchase.group_purchase_user`), Website: Restricted Editor (`website.group_website_restricted_editor`), full Accounting (`account.group_account_user`) |

These mappings (which "Sales: User" level, which "Website: Editor" level,
which Accounting groups) are recorded as **open decisions** in
`docs/decisions.md` - not yet confirmed against the senior's system.

## Assigning a role

Settings → Users & Companies → Users → open a user → Other tab (or the
Access Rights area) → under the **HealthyMed-Rolle** section, pick one of
the four roles. Only one role from this privilege can be active at a time,
same as any other Odoo privilege (Sales, Inventory, etc.).

## Extending it later

To add a fifth role or change what an existing role implies, edit
`security/healthymed_rollen_groups.xml` only - every role's `implied_ids`
list is the single place its standard groups are declared. Reference groups
by external ID (`module.xml_id`), never by name or database ID. Add the new
role's German label to `i18n/de.po` too.
