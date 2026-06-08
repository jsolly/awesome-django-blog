---
name: research
description: Use when the user says `/research`, asks for a deep-research prompt, mentions Perplexity Deep Research, or wants a copy/paste query for an external research tool instead of immediate analysis.
---

# Research Query Builder

Generate a single copy/paste-ready prompt for a deep research tool. The deliverable is the prompt, not the research results or the markdown report.

## Output Contract

If the request is specific enough, return exactly one fenced text block containing the prompt.

- No preamble
- No "Here's a prompt..."
- No postscript
- No second option unless the user asks for alternatives

If the request is underspecified in a way that would materially change the search quality, ask one concise clarifying question instead of guessing.

Ask only when a missing detail changes the answer meaningfully, such as:

- objective or decision to inform
- geography or jurisdiction
- timeframe
- comparison set
- intended audience

Do not ask a questionnaire. Ask one question, then continue.

## What the Prompt Should Do

Build a prompt that makes the downstream research tool:

- answer the actual question, not just the topic area
- prioritize primary sources where possible
- use secondary synthesis only to triangulate or fill gaps
- separate observed evidence from forecasts or projections
- surface disagreement, uncertainty, and known debates
- link or cite consequential claims
- organize the result in a markdown-friendly structure

Prefer explicit constraints over generic filler. Skip obvious instructions the model already knows.

## Prompt Pattern

Include the pieces that matter for this request:

1. The research objective
2. Scope boundaries
3. Geography or jurisdiction
4. Time range
5. Comparisons or alternatives
6. Preferred source types
7. Important disagreements or open questions
8. Desired markdown structure for the downstream result

When helpful, tell the tool to distinguish:

- current facts vs projections
- primary evidence vs commentary
- consensus vs disputed claims

## Defaults

Apply process defaults, not domain defaults.

- Default to primary sources first
- Ask for source links for major claims
- Ask for uncertainty and disagreement to be surfaced
- Ask for markdown sections such as executive summary, key findings, evidence, open questions, and source list

Do not invent missing domain scope. If the topic could plausibly mean several very different research tasks, clarify first.

## Gotchas

- Do not do the research yourself
- Do not write the markdown report yourself
- Do not wrap the prompt in extra explanation
- Do not silently narrow a vague request
- Do not ignore `/research` and drift into analysis mode
- Do not ask multiple clarification questions at once

If the user says `/research` and also asks for a report, honor the `/research` contract first: return the prompt that should generate the report.

## Example

User:

```text
/research Write me a markdown research report on CMS reimbursement for lactation services.
```

Response:

```text
Research CMS reimbursement for lactation services in the United States, with clear separation between Medicare, Medicaid, and Medicaid managed care. Focus on current billing and reimbursement pathways, eligible provider types, relevant CPT/HCPCS codes, supervision or incident-to constraints, telehealth applicability, and major state-by-state variation where it materially changes reimbursement. Prioritize primary sources first: CMS manuals, fee schedules, transmittals, state Medicaid policy documents, managed care guidance, and other official payer documents. Use secondary sources only to triangulate or explain gaps in primary guidance. Distinguish clearly between confirmed policy, common billing practice, and uncertain or state-specific interpretation. Surface disagreements or ambiguities, especially where provider eligibility, direct IBCLC billing, or code usage varies by payer or state. Organize the result in markdown with: 1) executive summary, 2) Medicare, 3) Medicaid fee-for-service, 4) Medicaid managed care, 5) billing pathways and codes, 6) state variation and operational constraints, 7) open questions or unresolved ambiguities, and 8) source list with links.
```
