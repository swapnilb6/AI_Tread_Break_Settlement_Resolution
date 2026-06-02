---
doc_name: audit policy
doc_type: POLICY
exception_type: AUDIT
market: ALL
version: v1.0
effective_date: 2026-01-01
---

# Purpose
This policy defines the minimum audit-trail requirements for the trade break and settlement exception resolution workflow.

# Audit Objectives
The audit record must allow an independent reviewer to answer:
- what happened
- what evidence was used
- what decision was made
- who or what made the decision
- whether approval was required and obtained
- what final outcome occurred

# Minimum Audit Record
Each case must capture:
- case_id / exception_id
- timestamps for intake, retrieval, recommendation, approval, and closure
- exception type
- root cause assessment
- alternative hypotheses if relevant
- final recommended action
- final approved action
- risk level
- confidence score
- citations to evidence
- tools used and tool outputs referenced
- human approval details if applicable
- final outcome and status

# Evidence Standards
Evidence recorded in the audit trail must be:
- attributable to a source
- time-bound where relevant
- sufficient to support the action
- preserved in a form suitable for later review

# Citation Requirements
Each material recommendation must include citations to:
- policy/SOP chunks from Chroma retrieval
- reference data used for the decision
- historical case evidence if relied upon

# Approval Audit Requirements
When human approval is required, record:
- approver identity
- approval status
- approval timestamp
- comments
- whether the approver corrected the action
- whether an override occurred

# Logging Guidance
Operational logs may summarize execution steps but should avoid unnecessary sensitive data exposure. If redaction is required, redact before persistence while preserving decision lineage.

# Version Tracking
Prompt versions, policy versions, and decision-policy versions should be traceable so later reviewers can reconstruct the decision context.

# Retention Guidance
Audit records should remain available for review throughout the project lifecycle and any required retention period defined by internal governance.

# Control Notes
Incomplete audit records are a control failure. If key evidence or approval data is missing, do not mark the case as fully resolved.
