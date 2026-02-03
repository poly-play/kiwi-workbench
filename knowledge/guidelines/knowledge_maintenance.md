# 🧠 Knowledge Maintenance Protocol (KMP)

> **Core Principle**: Documentation IS Code. Stale documentation is a bug.

This protocol defines how Agents and Humans should maintain the **Static Knowledge** (SOPs, Guidelines, Standards) within the `knowledge/` directory.

## 1. The "See Something, Say Something" Rule

**For Agents:**
When executing a task, if you discover that the actual system behavior (e.g., database schema, API response, business rule) differs from what is documented in `knowledge/`:
1.  **DO NOT** silently work around it.
2.  **STOP** and assess the discrepancy.
3.  **ACTION**:
    *   If you are confident: Update the relevant Markdown file immediately.
    *   If you are unsure: Raise a flag in your final report ("Discrepancy Detected").

**For Humans:**
If you change a business process manually, you MUST update the corresponding `knowledge/` file.

## 2. Update Lifecycle

### 2.1 Trigger
*   Code Refactoring -> Must check `README.md` / `domain_standards.md`.
*   New Feature -> Must add to `ops_manual.md`.
*   Feedback Loop -> If an operation fails, the "Fix" includes updating the SOP.

### 2.2 Verification
*   After updating a document, run a simulated "Mental Walkthrough" to ensure the new instructions are physically possible to execute.

## 3. Maintenance Checklist

When closing a complex task, run this check:

- [ ] Does `knowledge/scheduler.yaml` match the actual crontab?
- [ ] Do `domain_standards.md` reflect any new sub-domains added?
- [ ] Does `config.yaml` need new keys? (If so, add to L3/L4 config templates).
- [ ] Does `ops_manual.md` need a new example for this new feature?

---
*Follow this protocol to keep Kiwi's brain fresh.*
