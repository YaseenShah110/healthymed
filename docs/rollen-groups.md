# Roles and security groups (healthymed_rollen)

Source: the senior's build. No custom fields. Security groups only.

## Structure
- One privilege/category: HealthyMed
- One role group inside it: HealthyMed-Rolle
- Four roles. Each role is built ONLY by implying existing standard Odoo
  groups. No new permission logic, no new models, no record rules unless I ask.

## Roles
| Role | Meaning | Standard permissions it combines |
|---|---|---|
| Innendienst | Office staff | Sales: User. Inventory: User. |
| Lager und Versand | Warehouse and shipping | Inventory: User. Manage lots/serial numbers. Show lot number on delivery slip. |
| Buchhaltung | Accounting | Sales: User. Accounting/Invoicing. |
| Geschäftsführung | Management | Everything in Innendienst, Lager und Versand and Buchhaltung, plus Sales: Administrator, Purchase: User, Website: Editor, full Accounting. |

## Open point
The senior's system stores these roles as numeric group IDs: 23, 24, 27, 29,
36, 37, 40, 42, 50, 54. The names behind the IDs were not resolved. In
particular IDs 40 and 42 are probably "manage lots/serial numbers" and "show
lot number on delivery slip".
Claude must find the real Odoo 19 group names in the core source, propose the
mapping role by role, and ask me to confirm it before building. Never guess.
Never use database IDs in code. Reference groups by external ID.

## Tests required
One test user per role. For each role assert what it can and cannot read,
create or edit on sale.order, stock.picking, stock.lot, account.move,
purchase.order and the website editor, and that menus are visible or hidden as
expected.