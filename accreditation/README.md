# Accreditation fixtures

Example telemetry documents for the OpenAttribution Commerce Profile, and the runner that assesses them against the single Compliant tier.

These verify the document-checkable component of the profile: standard conformance at the Retrieval baseline (PROFILE.md section 5.1), `ctx_token` propagation across the click-out boundary (section 5.5), and the citation chain that makes multi-citation attribution possible (section 5.6). The operational requirements - delivery cadence, completeness, the consent gate on `ctx_token` resolution, the weighting model and its disclosure, and content-owner isolation (sections 5.2, 5.3, 5.6, 5.7) - are properties of the implementer's pipeline and cannot be fixture-tested. They are assessed separately by attestation and inspection.

## Layout

```
accreditation/
  validate.py    the assessment runner
  fixtures/      Content Telemetry documents, each declaring its expected outcome
```

## Running

```sh
python3 validate.py
```

No dependencies. Exit code 0 means every fixture was assessed at its expected outcome.

## How a fixture is assessed

Each fixture is a Content Telemetry document - a session document or a standalone event. The runner checks:

- **Retrieval baseline** (PROFILE.md section 5.1): every event has `type` and `timestamp`, every content event carries at least one of `content_url` or `content_id`, and every `content_retrieved` event carries `source_role`.
- **ctx_token propagation** (section 5.5): a cross-boundary click-out engagement (`link_click` or `agent_navigate`) carries a `ctx_token` and never a raw `session_id`.
- **Multi-citation support** (section 5.6): a commerce flow that reports a click-out also records the `content_grounded`, `content_cited`, and `content_displayed` events behind it, so a click manifest can be built.

A document that passes every applicable check is assessed Compliant. A document that fails any check reaches no tier.

The runner assumes fixtures are well-formed Content Telemetry documents; validating a document against the JSON Schema is the [standard repository's](https://github.com/SPUR-Coalition/telemetry) test suite.

## Fixture format

Each fixture carries annotation fields alongside the telemetry document:

- `_test_description` - what the fixture demonstrates
- `_test_expected_tier` - the outcome the document should be assessed at: `"compliant"` or `null` when the document reaches no tier
- `_test_expected_reason` - for non-compliant fixtures, a substring of the expected blocking reason

Content Telemetry consumers tolerate unknown fields, so these annotations do not affect the document's validity.

## What the suite covers

| Fixture | Expected | Demonstrates |
|---------|----------|--------------|
| `commerce-full-flow-multicitation` | Compliant | Two sources grounded, cited, and displayed; click-out with `ctx_token` |
| `destination-clickout-with-ctx-token` | Compliant | Destination-side standalone click-out carrying a `ctx_token` |
| `destination-clickout-agent-navigate` | Compliant | Agent-mediated click-out (`agent_navigate`) with a `ctx_token` |
| `destination-clickout-no-ctx-token` | No tier | Click-out with no `ctx_token` - unresolvable to a session |
| `destination-clickout-leaks-session-id` | No tier | Click-out carrying a raw `session_id` across the boundary |
| `commerce-clickout-no-citation-chain` | No tier | Click-out with no citation chain behind it |
