# Content Telemetry Extension for UCP

**Extension name:** `org.openattribution.telemetry`
**Version:** `2026-02-17`
**Extends:** `dev.ucp.shopping.checkout`
**Status:** Draft

## Overview

This extension augments UCP checkout sessions with content attribution telemetry. When an AI agent helps a user make a purchase, the extension records which content the agent retrieved and cited on the way to the sale, so attribution systems can credit the sources that informed the recommendation.

## Why this exists

AI commerce is opaque. When a shopping agent recommends a product, the recommendation is informed by reviews, guides, comparisons, and other content. Currently:

- Content creators have no visibility into whether their work influenced purchases
- Merchants can't measure which content partnerships drive ROI
- Attribution algorithms have no standardised signal to work with

This extension provides the telemetry layer. Attribution algorithms, payment structures, and business agreements remain outside scope.

## Capability declaration

Merchants and agents declare support in their UCP profile:

```json
{
  "ucp": {
    "capabilities": [
      {
        "name": "dev.ucp.shopping.checkout",
        "version": "2026-01-11"
      },
      {
        "name": "org.openattribution.telemetry",
        "version": "2026-02-17",
        "spec": "https://openattribution.org/telemetry/ucp/extension",
        "schema": "https://openattribution.org/telemetry/ucp/schemas/extension.json",
        "extends": "dev.ucp.shopping.checkout"
      }
    ]
  }
}
```

The `spec` and `schema` URLs identify the extension under the `openattribution.org` namespace and are reserved; they do not resolve yet. The authoritative copies are this document and [`extension-schema.json`](./extension-schema.json) in this repository.

## Schema

The extension adds an `attribution` object to checkout sessions:

```json
{
  "id": "chk_123456789",
  "status": "ready_for_complete",
  "line_items": ["..."],
  "totals": ["..."],

  "attribution": {
    "content_scope": "running-reviews",
    "content_retrieved": [
      {
        "content_url": "https://www.runnersworld.com/gear/best-running-shoes",
        "timestamp": "2026-01-20T14:10:01Z"
      },
      {
        "content_url": "https://www.believeintherun.com/shoe-reviews",
        "timestamp": "2026-01-20T14:10:02Z"
      }
    ],
    "content_cited": [
      {
        "content_url": "https://www.runnersworld.com/gear/best-running-shoes",
        "timestamp": "2026-01-20T14:10:05Z",
        "citation_type": "paraphrase",
        "excerpt_tokens": 72,
        "position": "primary"
      }
    ],
    "conversation_summary": {
      "turn_count": 4,
      "topics": ["running-shoes", "cushioning", "stability"]
    }
  }
}
```

## Fields

### `attribution.content_scope`

Opaque identifier for the content collection used. Meaning is implementer-defined:

| Implementation | Example value |
|----------------|---------------|
| Content mix platform | `"electronics-reviews-mix"` |
| API key scoped | `"apikey_abc123"` |
| Agreement ID | `"agreement_456"` |

**Requirements:**

- MUST NOT contain personally identifiable information (PII) or be derivable to PII
- SHOULD be stable across sessions to enable cross-session aggregation
- Consumers MUST NOT attempt to reverse-engineer the content collection from the scope value

### `attribution.content_retrieved`

Content fetched during the session. Captures correlation (content was available) without claiming causation (content was used). Required - if you're sending `attribution`, you must have retrieved something.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `content_url` | string (URI) | Yes | URL of the content retrieved |
| `timestamp` | datetime | Yes | When retrieved (UTC) |

For multi-conversation attribution (user researches Monday, buys Friday), agents accumulate all relevant content from prior conversations into the final checkout's `content_retrieved` array. Timestamps on entries provide the temporal signal.

### `attribution.content_cited`

Content explicitly referenced in agent responses. Includes quality signals for more accurate attribution:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `content_url` | string (URI) | Yes | URL of the content cited |
| `timestamp` | datetime | Yes | When cited (UTC) |
| `citation_type` | enum | No | How content was used |
| `excerpt_tokens` | integer | No | Token count of excerpt |
| `position` | enum | No | Prominence in response |
| `content_hash` | string | No | SHA-256 integrity audit trail |

#### Citation types

| Type | Description |
|------|-------------|
| `direct_quote` | Verbatim or near-verbatim |
| `paraphrase` | Restated in different words |
| `reference` | Mentioned without quoting |
| `contradiction` | Retrieved but disagreed with |
| `unclassified` | The agent did not classify this citation |

These are agent-reported metadata describing how content appeared in a response. How each type is weighted for attribution is left to the consuming analytics platform.

#### Position

| Position | Description |
|----------|-------------|
| `primary` | Main basis for the response |
| `supporting` | Additional evidence |
| `mentioned` | Referenced but not relied upon |
| `unclassified` | The agent did not determine prominence |

#### Content hash

SHA-256 hash of the content the agent processed from the cited URL, for integrity audit trail in dispute resolution. The spec does not prescribe the extraction method - agents hash whatever content they fed into their context. Agents SHOULD use a consistent hashing method across citations within a session.

### `attribution.conversation_summary`

Lightweight conversation context. All fields are agent-reported hints.

| Field | Type | Description |
|-------|------|-------------|
| `turn_count` | integer | Number of conversation turns before checkout (minimum 1) |
| `topics` | array of strings | De-duplicated free-form topic tags from the conversation |

`turn_count` provides a signal of conversation depth that is not derivable from the citation arrays. `topics` provides lightweight category tags that help merchants route attribution internally without needing to crawl the cited URLs.

## Negotiation

When agent and merchant both declare `org.openattribution.telemetry`:

1. Agent populates `attribution` object during checkout session
2. Merchant includes `attribution` in checkout response
3. On `checkout_completed`, attribution data flows to outcome

When only one party supports the extension:

- **Agent supports, merchant doesn't:** Agent can still collect telemetry client-side for its own attribution
- **Merchant supports, agent doesn't:** Merchant receives checkout without `attribution` object; no server-side attribution data

Graceful degradation: the checkout proceeds normally regardless. Attribution is additive, not blocking.

## Privacy considerations

### Data minimisation

- `conversation_summary` provides attribution signals without raw conversation text
- `content_scope` is opaque - doesn't reveal content collection contents

### Privacy levels

For implementations that need more granular control, the Content Telemetry standard defines privacy levels (`full`, `summary`, `intent`, `minimal`).

The checkout extension operates at `summary`-equivalent level by default - `conversation_summary` contains only `turn_count` and `topics`, both of which are safe to share at all privacy levels. Implementations MAY negotiate a different privacy level through out-of-band agreements.

## Relationship to the Content Telemetry spec

This extension is a UCP binding of [Content Telemetry v0.1](https://contenttelemetry.org). The canonical specification is protocol-independent and stewarded by the SPUR Coalition; this binding is maintained by OpenAttribution. The standalone spec supports:

- Non-UCP contexts (direct API, MCP tools)
- Full conversation turn data with privacy levels
- Agent-to-agent session linking

This extension takes the commerce-relevant subset and packages it for UCP's `allOf` composition model.

## Example: full checkout with attribution

```json
{
  "ucp": {
    "version": "2026-01-11",
    "capabilities": [
      { "name": "dev.ucp.shopping.checkout", "version": "2026-01-11" },
      { "name": "org.openattribution.telemetry", "version": "2026-02-17" }
    ]
  },
  "id": "chk_skincare_purchase",
  "status": "completed",
  "line_items": [
    {
      "id": "li_1",
      "item": {
        "id": "cerave_moisturising_cream_340g",
        "title": "CeraVe Moisturising Cream 340g",
        "price": 1499
      },
      "quantity": 1
    }
  ],
  "totals": [
    { "type": "subtotal", "amount": 1499 },
    { "type": "total", "amount": 1499 }
  ],
  "currency": "GBP",

  "attribution": {
    "content_scope": "skincare-reviews",
    "content_retrieved": [
      {
        "content_url": "https://www.carolinehirons.com/2025/12/cerave-moisturising-cream-review",
        "timestamp": "2026-01-18T09:15:01Z"
      },
      {
        "content_url": "https://theskincareedit.com/cerave-moisturising-cream-review",
        "timestamp": "2026-01-18T09:15:02Z"
      },
      {
        "content_url": "https://www.beautybible.com/best-ceramide-moisturisers",
        "timestamp": "2026-01-18T09:16:00Z"
      }
    ],
    "content_cited": [
      {
        "content_url": "https://www.carolinehirons.com/2025/12/cerave-moisturising-cream-review",
        "timestamp": "2026-01-18T09:15:05Z",
        "citation_type": "paraphrase",
        "excerpt_tokens": 92,
        "position": "primary",
        "content_hash": "sha256:b2c3d4e5f67890abcdef1234567890abcdef1234567890abcdef1234567890ab"
      },
      {
        "content_url": "https://theskincareedit.com/cerave-moisturising-cream-review",
        "timestamp": "2026-01-18T09:15:06Z",
        "citation_type": "reference",
        "position": "supporting"
      }
    ],
    "conversation_summary": {
      "turn_count": 3,
      "topics": ["moisturiser", "dry-skin", "ceramides"]
    }
  }
}
```

## Implementation notes

### For agent developers

1. Check merchant profile for `org.openattribution.telemetry` support
2. If supported, populate `attribution` during checkout session
3. Track content retrieval and citation during conversation
4. For purchases spanning multiple conversations, accumulate all relevant content into the final checkout's `content_retrieved` array

### For merchants

1. Declare capability in `/.well-known/ucp` profile
2. Accept and store `attribution` from checkout requests
3. Include `attribution` in checkout responses
4. Forward to attribution system on `checkout_completed`

### For attribution systems

1. Consume `attribution` data from completed checkouts
2. Use `content_cited` with quality signals for weighted attribution
3. Use `content_retrieved` timestamps for temporal attribution when research spans days
4. Aggregate by `content_scope` for mix-level analytics

## Changelog

### 2026-02-17

- Removed `prior_session_ids` from checkout extension (privacy concern; agents accumulate content into `content_retrieved` instead)
- Stripped `conversation_summary` to `turn_count` + `topics` only (removed `primary_intent`, `total_content_retrieved`, `total_content_cited`)
- Added `content_retrieved` to required fields with `minItems: 1`
- Reframed `content_hash` as integrity audit trail; relaxed regex to mixed-case hex
- Added `$comment` provenance linking to canonical OpenAttribution spec

### 2026-02-11 (Draft)

- Initial extension specification
- Based on Content Telemetry v0.1
- Extends `dev.ucp.shopping.checkout`
