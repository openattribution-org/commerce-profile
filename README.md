# OpenAttribution Commerce Profile

**Commerce-facing requirements for the OpenAttribution Telemetry standard.**

This directory is a **draft profile**. It names a single accreditation tier - Compliant - and the requirements an implementer in agentic commerce (affiliate networks, marketplaces, brands, destination sites) must meet to be assessed at it: conformance to the standard, event-level and real-time delivery, click-out reporting, `ctx_token` propagation across the click boundary, multi-citation attribution, and - for attribution consumers - resolving a `ctx_token` to a privacy- and consent-gated click manifest.

The **standard** - the telemetry wire format itself - lives in [openattribution-org/telemetry](https://github.com/openattribution-org/telemetry). This profile references the standard by version and does not restate it.

## The point of this profile

A click from an AI agent's response is the end of a chain of sources, not a single referrer. The agent read several reviews and guides, cited some, displayed some, and the user clicked one link. This profile keeps that chain intact across the boundary between the agent and the landing page, so a destination can credit every source that informed the response - multi-citation attribution - rather than only the clicked URL.

The mechanism is the standard's `ctx_token`: an opaque click-token the agent issues, carried to the landing page in place of the session identifier, which an attribution consumer resolves to the click manifest (the session's grounded, cited, and displayed sources). The session UUID never crosses the boundary.

## Why a separate profile

The standard is permissive and value-neutral; this profile adds commerce-specific requirements on top. The dependency runs one way - profile to standard, never the reverse - so the standard can move to a neutral standards body without disturbing this profile, which simply updates its version reference. The profile names no operator and no hosted endpoint: a competing operator can implement and be assessed against it with no dependency on any single operator's infrastructure.

## What's in this directory

- [PROFILE.md](./PROFILE.md) - the profile: requirements, conformance assessment, conformance mark
- [accreditation/](./accreditation/) - example fixtures and the assessment runner

## Compliant at a glance

| Requirement | Means |
|-------------|-------|
| Conformance to the standard | Conforming emitter at Retrieval, Grounding, or Attribution level |
| Event-level delivery | Discrete events per fetch / grounding / citation / display / engagement - no aggregation |
| Real-time delivery | Events dispatched as they occur; alternative cadence by negotiation |
| Click-out reporting | Click-outs reported as `content_engaged` / `link_click` events |
| ctx_token propagation | Cross-boundary `link_click` carries a `ctx_token`, never the raw `session_id` |
| Multi-citation attribution | Credit every source in the click manifest, not only the clicked URL |

Attribution consumers meet a parallel set (PROFILE.md section 5.7): standard consumer conformance, `ctx_token` resolution to a privacy- and consent-gated click manifest, and content-owner resolution and isolation.

## Running the accreditation suite

```sh
python3 accreditation/validate.py
```

No external dependencies. Exit code 0 means every fixture's assessed tier matched its declared expectation.

## Status

Draft (v0.1). Constrains OpenAttribution Telemetry v0.1. The two standard additions this profile relies on - the `ctx_token` field and its click-manifest resolution semantics - have landed in the telemetry standard ([openattribution-org/telemetry#4](https://github.com/openattribution-org/telemetry/pull/4)); the profile's one-way dependency on the standard is clean once that merges. Requirements may change before 1.0.
