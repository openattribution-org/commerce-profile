# OpenAttribution Commerce Profile

Commerce-facing requirements for the OpenAttribution Telemetry standard.

**Version:** 0.1
**Status:** Draft
**Last updated:** 2026-05-29
**Constrains:** OpenAttribution Telemetry specification, version 0.1

## Contents

1. [Scope](#1-scope)
2. [Normative references](#2-normative-references)
3. [Terms and definitions](#3-terms-and-definitions)
4. [Relationship to the OpenAttribution Telemetry standard](#4-relationship-to-the-openattribution-telemetry-standard)
5. [Requirements](#5-requirements)
6. [Conformance assessment](#6-conformance-assessment)
7. [The OpenAttribution Commerce conformance mark](#7-the-openattribution-commerce-conformance-mark)
8. [Versioning](#8-versioning)

## Introduction

The OpenAttribution Telemetry standard defines a wire format for reporting how AI agents use content. The format is permissive: an emitter producing well-formed events at any conformance level is conforming to the standard.

This profile is the commerce-facing layer. It applies to participants in agentic commerce: affiliate networks, marketplaces, brands, and destination sites that receive AI-driven traffic and want to attribute it to the content that produced it. It names a single accreditation tier, Compliant, and the requirements an implementer must meet to be assessed at it.

When an AI agent recommends a product, that recommendation was shaped by content the agent read: reviews, comparison guides, editorial recommendations. The agent retrieves that content, grounds it, cites some of it, displays some of it, and the user clicks through to a destination. A single click is the end of a chain of sources, not a single referrer. This profile exists to keep that chain intact across the boundary between the agent and the landing page, so a destination can credit every source that informed the response, not only the one URL the user happened to click.

The mechanism is the standard's `ctx_token` (standard, section 7.1): an opaque click-token the agent issues, which crosses to the landing page in place of the session identifier, and which an attribution consumer resolves to the originating session. This profile requires that propagation and the consumer-side resolution that makes it useful.

The standard and this profile are maintained separately. The standard defines the format; this profile defines the commerce-facing requirements layered on it. This profile adds requirements; it never modifies the wire format.

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) and [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174).

## 1. Scope

This document specifies:

- the requirements an implementer must meet to be assessed as OpenAttribution Commerce Compliant
- how an implementer is assessed against those requirements
- the conditions for displaying the OpenAttribution Commerce conformance mark

This document does not specify:

- the telemetry wire format - event types, schema, conformance levels, transport (see the OpenAttribution Telemetry specification, the normative reference in section 2)
- attribution algorithms, counting models, or commission logic
- content access, licensing, or pricing terms
- privacy policies or data protection requirements
- any operator's account model, API endpoints, or hosted infrastructure

## 2. Normative references

| Reference | Description |
|-----------|-------------|
| OpenAttribution Telemetry specification, version 0.1 | The telemetry wire format this profile constrains. <https://github.com/openattribution-org/telemetry> |
| RFC 2119 | Key words for use in RFCs to indicate requirement levels |
| RFC 8174 | Ambiguity of uppercase vs lowercase in RFC 2119 key words |

This profile constrains a fixed version of the OpenAttribution Telemetry specification. Where this document refers to "the standard", it means version 0.1 as cited above. Adoption of a later standard version is a deliberate revision of this profile (section 8).

## 3. Terms and definitions

The terms defined in the OpenAttribution Telemetry specification section 3 apply. In addition, for the purposes of this document:

### 3.1

**profile**

document that layers community-specific requirements on a standard

### 3.2

**Compliant**

named tier of accreditation under this profile - meeting every requirement in section 5

### 3.3

**accredited implementer**

emitter or attribution consumer assessed as meeting this profile's requirements

### 3.4

**conformance mark**

visual mark an OpenAttribution Commerce-accredited implementer may display to indicate Compliant status (section 7)

### 3.5

**click-out**

a user following an outbound link from an AI agent's response to a destination site, marketplace, or brand

### 3.6

**ctx_token**

opaque click-token issued by the originating agent and carried on a `content_engaged` event in place of `session_id` when the engagement crosses to a landing page (standard, section 7.1)

### 3.7

**click manifest**

the set of `content_grounded`, `content_cited`, and `content_displayed` events for the session resolved from a `ctx_token` - the citation chain behind a click (standard, section 7.1, ctx_token resolution)

### 3.8

**multi-citation attribution**

crediting every source in the click manifest for a click-out, rather than only the single clicked URL (section 5.6)

## 4. Relationship to the OpenAttribution Telemetry standard

The standard defines the wire format. This profile selects from it and adds requirements specific to commerce.

The standard defines three conformance levels - Retrieval, Grounding, and Attribution (standard, section 5.7) - a privacy mechanism with four levels (standard, section 5.5), the `ctx_token` click-out mechanism and its resolution (standard, section 7.1). The standard makes none of these mandatory for any relationship.

This profile builds on the standard's mechanisms without changing them. An implementer that meets this profile's requirements is, by construction, conforming to the standard. An implementer can conform to the standard without engaging with this profile at all.

The dependency runs one way - profile to standard, never the reverse. The standard can therefore be transferred to another steward without disturbing this profile: the profile updates its section 2 reference to the standard's new location and version. This profile names no operator, no hosted endpoint, and no operator-specific API. Every requirement is expressed against the standard's mechanisms, so a competing operator can implement and be assessed against this profile with no dependency on any single operator's infrastructure.

## 5. Requirements

An implementer assessed as OpenAttribution Commerce Compliant MUST meet every requirement below that applies to it: an emitter against sections 5.1 through 5.4 and 5.5, an attribution consumer against section 5.7. Multi-citation attribution (section 5.6) is the requirement that distinguishes this profile.

### 5.1 Conformance to the standard

The implementer MUST be a conforming emitter to the OpenAttribution Telemetry specification at any conformance level - Retrieval, Grounding, or Attribution. Conformance is verified against the standard's reference test suite (standard, section 5.7).

A destination site reporting click-out engagement events qualifies at the Retrieval level for those events. An agent reporting the full lifecycle from retrieval through engagement qualifies at the Attribution level. Both are Compliant under this profile where they meet the commerce requirements below.

### 5.2 Event-level delivery

Telemetry MUST be delivered at event granularity. Each fetched, grounded, cited, displayed, or engaged content piece is reported as a discrete event, with the fields the standard requires at the implementer's conformance level.

Aggregated reporting - summaries, counts, or rollups that collapse multiple events into a single record - does not satisfy this requirement. Aggregation, where useful, is performed by the receiving party on event-level input.

### 5.3 Real-time delivery

The implementer MUST be capable of delivering telemetry in real time. Real-time means events are dispatched to the receiving endpoint as they occur, subject only to ordinary network and processing latency.

A commerce relationship MAY negotiate an alternative delivery cadence in a specific agreement. The standard supports both modes; this profile sets real time as the default and lets bilateral agreements vary it.

### 5.4 Click-out engagement reporting

An implementer that observes a click-out from an AI agent's response to a landing page - typically an affiliate network, marketplace, or destination site - MUST report it as a `content_engaged` event with `engagement_type: link_click`, carrying the event-level `content_url` of the clicked destination (standard, section 6.7).

This is the event that anchors commerce attribution: it records that a user acted on the agent's response. Reporting it is unconditional. Whether the citation chain behind it can be read is a separate, consent-gated matter (section 5.7.2).

### 5.5 ctx_token propagation across the click-out boundary

On a `content_engaged` event with `engagement_type: link_click` that crosses to a landing page after a click-out, the implementer MUST propagate the session linkage using the `ctx_token` mechanism (standard, section 7.1): the event carries a `ctx_token` issued by the originating agent in place of `session_id`.

The implementer MUST NOT carry the raw `session_id` across the agent-to-landing-page boundary. The `ctx_token` is opaque and resolvable only by an attribution consumer, so the session identifier is not exposed to the destination or to any party observing the outbound link. An implementer that emits a cross-boundary `link_click` engagement with neither `ctx_token` nor a resolvable session linkage does not meet this requirement.

### 5.6 Multi-citation attribution

The point of this profile is that a click-out credits the whole citation chain, not only the clicked URL.

An implementer performing attribution on a click-out MUST be capable of crediting every source in the click manifest (section 3.7): the `content_grounded`, `content_cited`, and `content_displayed` events of the session resolved from the `ctx_token`. It MUST NOT restrict attribution to the single `content_url` carried on the `link_click` event when the click manifest is available.

The click manifest is the set of those events for the resolved session; the implementer weights them under its own counting model. This profile does not mandate the algorithm - last-touch, linear, position-based, or any other model in the standard's section 10 is permitted - only that every source in the manifest is eligible for credit. A destination that resolves a `ctx_token` and credits only the clicked URL, discarding the other grounded and cited sources, is not Compliant.

The manifest reflects only what privacy and consent permit (section 5.7.2). Sources withheld by `privacy_level` gating or by a missing consent opt-in are not in the manifest and cannot be credited; this is a property of the data the implementer receives, not a relaxation of this requirement.

### 5.7 Attribution consumer requirements

Sections 5.1 through 5.6 govern emitters and the parties that perform attribution on received events. An attribution consumer - a party that receives telemetry and resolves `ctx_token`s to click manifests (standard, section 7.3 and section 7.1) - is assessed against the requirements below. The multi-citation requirement in section 5.6 relies on them.

#### 5.7.1 Conformance to the standard

The consumer MUST meet the attribution-consumer conformance rules of the OpenAttribution Telemetry specification (standard, section 5.7): accept any session with a compatible schema version, tolerate unknown fields and events from any conformance level, accept both the session-document and standalone-event delivery formats and reconstruct sessions from standalone events, and strip privacy-violating fields rather than reject the document carrying them.

#### 5.7.2 ctx_token resolution to a click manifest

The consumer MUST support resolving a `ctx_token` to the click manifest of the originating session: the set of `content_grounded`, `content_cited`, and `content_displayed` events for that session (standard, section 7.1, ctx_token resolution).

The manifest the consumer returns:

- MUST be gated by the resolved session's `privacy_level` (standard, section 5.5). Fields and sources not available at that level MUST NOT appear in the manifest.
- MUST be gated by two-sided consent. The consumer MUST return the manifest only when the agent that issued the token has opted in to sharing sessions via click tokens and the content owner whose URLs appear has opted in to being visible in click-token lookups. When either opt-in is absent, the consumer MUST NOT disclose the manifest for the affected source. The mechanism by which an agent and a content owner record these opt-ins is operator-defined; the consent gate itself is required.

A consumer that returns a clicked URL but cannot return the rest of the citation chain does not satisfy this requirement and cannot support the multi-citation attribution that section 5.6 requires of the parties it serves.

#### 5.7.3 Publisher resolution and isolation

The consumer MUST resolve the owning content owner for each event and expose to a given party only the events that party is entitled to. A content owner's identifiable telemetry MUST NOT be disclosed to another party without that content owner's authorisation. This is the same isolation the standard relies on for multi-content-owner sessions (standard, section 7.3); resolving a `ctx_token` does not override it - the click manifest is itself gated by section 5.7.2.

Aggregate or anonymised reporting across a catalogue - benchmarks that do not reveal an individual content owner's content usage - is not restricted by this requirement.

## 6. Conformance assessment

An implementer is assessed as OpenAttribution Commerce Compliant when it meets every requirement in section 5 that applies to it: an emitter against sections 5.1 through 5.6, an attribution consumer against section 5.7. Assessment has two parts:

1. **Technical conformance** - verified against the standard's reference test suite, for the conformance level an emitter advertises (5.1) or against the standard's attribution-consumer rules for a consumer (5.7.1), plus the commerce-specific document checks in the [`accreditation/`](./accreditation/) suite: a cross-boundary `link_click` engagement carries a `ctx_token` and not a raw `session_id` (5.5), and a conforming commerce flow records the grounded, cited, and displayed sources that make a click manifest possible (5.6). An objective, repeatable check.
2. **Operational requirements** - event-level granularity and real-time delivery (5.2, 5.3), `ctx_token` resolution to a privacy- and consent-gated click manifest (5.7.2), multi-citation crediting of the manifest (5.6), and content-owner resolution and isolation (5.7.3), verified by inspection of the implementer's pipeline and by attestation.

The [`accreditation/`](./accreditation/) directory holds example fixtures: telemetry documents that do and do not satisfy the document-checkable component of this profile. Operational requirements - cadence, the consent gate, the weighting model, and content-owner isolation - cannot be fixture-tested and are assessed separately.

Assessment is self-attested in this draft version. An independent audit programme is anticipated; the profile will be revised to require opt-in to it once available.

## 7. The OpenAttribution Commerce conformance mark

An OpenAttribution Commerce-accredited implementer may display the OpenAttribution Commerce conformance mark.

- The mark indicates the implementer is assessed as OpenAttribution Commerce Compliant.
- The mark refers to a specific version of this profile. An implementer reassessed against a later profile version updates the mark accordingly.
- OpenAttribution may withdraw the right to display the mark from an implementer that no longer meets the requirements.

The conformance mark is a trademark of OpenAttribution. Permission to display it is granted through accreditation and is separate from the licence that covers this document. The licence does not grant any right to use the mark or other OpenAttribution trademarks; that right is conveyed only through accreditation.

Mark artwork and detailed display rules are published separately by OpenAttribution.

## 8. Versioning

This profile is versioned independently of the standard it constrains.

Draft and preview versions (0.x) may change the requirements as the accreditation programme develops. From 1.0 onward, a change that adds, removes, or materially alters a requirement is a major version change.

This profile constrains a fixed version of the standard (section 2). When the OpenAttribution Telemetry standard publishes a new version, the working group decides whether this profile adopts it. Adoption is a deliberate revision: the section 2 reference changes, and the change is published as a new profile version. The standard advancing does not change this profile until the profile is revised to follow it.

If stewardship of the standard transfers to another body, this profile updates its section 2 reference to the standard's new name and location. The requirements are unaffected - they reference conformance levels, event semantics, and the `ctx_token` mechanism, which are properties of the format, not of its steward.
