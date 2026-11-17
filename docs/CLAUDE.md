Task 0: Governance and source documents. Branch feature/00-governance
(already created; continue on it).

1. Read CLAUDE.md, docs\scope.md, docs\field-spec.md and docs\rollen-groups.md
   completely. Scan all docs for passwords, API keys or logins. If you find any,
   replace them with [REDACTED] and tell me where.
2. Create docs\field-spec.json: a machine-readable version of field-spec.md.
   One entry per field or model with: module, model, field name, type, label,
   relation, selection values, required, readonly, size, computed/related notes.
   It will drive the parity test in Task 20.
3. Create docs\module-map.md: the 10 modules, their dependencies (from CLAUDE.md),
   what each contains, and the order they are built.
4. Create docs\scope-matrix.md with columns: ID, source (contract clause or
   "field-spec"), requirement, module or place, test, evidence, status. Number
   IDs by area (D design, W shop, E ERP, P product data, M supplier, R regional,
   S SSB, X beyond contract, N not included). One row per scope bullet in
   docs\scope.md sections 3.1 to 3.8. Mark each row: in contract, beyond
   contract (present in field-spec but not in the contract), not our part
   (SEO, training, go-live), excluded (as the contract lists), or external
   dependency (supplier API). Add rows for every field-spec feature that goes
   beyond the contract (SSB gate, KV regions, minimum order, invoice gating,
   return requests, ordered-by note).
5. Create docs\decisions.md: a decisions table (date, decision, why) and an
   "Open questions" section with at least these: relation behind
   x_is_regional_order; the rule behind x_invoice_allowed; rating.mixin on
   return requests; group names behind the role IDs; where the prescription
   part number for sutures comes from (no field exists); how the SSB
   prescription wait interacts with the supplier order; whether a scraper
   exists as code or only the file feed; the x_pzn dependency of
   megro_import; whether the senior's KV region data may be exported as
   configuration. Add any further contradictions you find between the documents.
6. Verify that .gitignore, ruff.toml and the pull request template exist. Report
   what is missing; do not fix it in this task.
7. Write NO Odoo code and run NO Odoo commands in this task.
8. Commit with "[ADD] docs: JSON spec, module map, scope matrix, decisions",
   push the branch and prepare the pull request text.

Report in the format required by CLAUDE.md. Then wait for my answers.