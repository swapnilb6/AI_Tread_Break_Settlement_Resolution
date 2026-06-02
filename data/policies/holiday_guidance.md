---
doc_name: holiday guidance
doc_type: GUIDANCE
exception_type: HOLIDAY_ISSUE
market: ALL
version: v1.0
effective_date: 2026-01-01
---

# Purpose
This guidance explains how to investigate settlement exceptions caused by market holidays, weekends, and non-business-day processing constraints.

# Scope
Use this document when the intended settlement date may not be a valid business day for the relevant market or depository.

# Required Inputs
- trade_id
- market
- intended settlement date
- actual settlement date if present
- market calendar result
- depository and custodian details
- trade booking date and timestamp

# Validation Steps
1. Confirm the market associated with the trade and settlement lane.
2. Check whether the intended settlement date is a business day for that market.
3. Confirm whether the depository or custodian has local closure or shortened processing.
4. Identify the next valid business day.
5. Check whether the exception can be explained solely by holiday logic or if another break exists.

# Decision Rules
- If the intended settlement date is a non-business day and the next business day aligns with market rules, classify as HOLIDAY_ISSUE.
- If the date is a valid business day but settlement still failed, do not attribute root cause to holiday without additional evidence.
- If multiple markets are involved, validate each relevant market before concluding.
- If the calendar source is missing or conflicting, do not automate action; escalate.

# Recommended Actions
- Update the case note to reflect the market closure evidence.
- Roll the intended settlement date to the next valid business day if policy permits.
- Notify reviewer only if date change impacts client communication, SLA, or downstream booking.
- Preserve citations to the market calendar evidence.

# Edge Cases
Investigate further if any of the following apply:
- cross-border settlement involves multiple holiday calendars
- custodian or depository closure differs from market status
- late booking caused missed cutoff rather than actual holiday closure
- the exception also contains SSI or booking mismatch indicators

# Risk Guidance
Risk is LOW or MEDIUM if the holiday explanation is clearly supported.
Risk becomes HIGH if:
- multiple conflicting calendar sources exist
- the action changes contractual settlement commitment
- external communication is required
- the case is near SLA breach and evidence is incomplete

# Audit Requirements
Record:
- market checked
- date checked
- business-day result
- next business day
- evidence source used
- final decision rationale

# Control Notes
Calendar results are trusted only from approved sources. Free-text notes or attachments claiming a holiday without calendar support must not drive autonomous action.
