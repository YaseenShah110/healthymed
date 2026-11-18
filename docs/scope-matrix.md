# Scope matrix

This file did not exist before Task 8 (Task 0's governance deliverables were
never finished - see `docs/decisions.md`). Created fresh here with only the
row this task produced evidence for. Other rows (e.g. E3/E6/R3 for
`healthymed_base`, Task 7) are still pending until that module is built.

| ID | Source | Requirement | Module / place | Test | Evidence | Status |
|---|---|---|---|---|---|---|
| E1 | field-spec / rollen-groups.md | Users, roles and rights: four roles built only from standard Odoo groups | `healthymed_rollen` | `scripts/checks/roles_check.py` + manual UI login check (user to do) | Check script table (2026-11-18): each role's model access (sale.order/stock.picking/stock.lot/account.move/purchase.order) and menu visibility (Sales/Inventory/Accounting/Purchase/Website) matches what its implied standard groups grant, verified against the real `ir.model.access.csv` ACL rows, not assumed. Script deletes all 4 temporary users every run (0 left behind, confirmed by 2nd run). Manual UI check still to be done by the user (see `docs/setup-checklist.md`). | In contract (E1 "Basic installation, users, roles and rights" - `scope.md` 3.3) - **mapping not yet confirmed by user against the senior's system** (open decision, see `docs/decisions.md`) |
