#!/usr/bin/env python3
"""Accreditation assessment for the OpenAttribution Commerce Profile.

This profile defines a single tier - Compliant - layered on the Content
Telemetry standard. The base technical requirement (PROFILE.md section 5.1) is
that the implementer emits valid Content Telemetry documents; where it advertises
a standard conformance level, Retrieval is the cheapest to satisfy and Grounding
and Citation are cumulative on it.

On top of that base, this profile adds commerce-specific requirements that ARE
checkable from a telemetry document:

  - ctx_token propagation (PROFILE.md section 5.5): a content_engaged event with
    engagement_type 'link_click' or 'agent_navigate' that crosses to a landing
    page MUST carry a ctx_token and MUST NOT carry a raw session_id. We detect
    the cross-boundary case as a standalone click-out engagement (document_type
    'event'), which is how a destination or network reports a click-out, and a
    click-out engagement inside a session that carries an explicit ctx_token.

  - multi-citation support (PROFILE.md section 5.6): a conforming commerce flow
    records the sources behind the click - content_grounded / content_cited /
    content_displayed events - so a click manifest can be built. A flow that
    reports a click-out with no citation chain behind it cannot support
    multi-citation attribution.

The remaining requirements - real-time cadence, the two-sided consent gate on
ctx_token resolution, the weighting model, and content-owner isolation
(PROFILE.md sections 5.3, 5.7.2, 5.7.3) - are properties of the implementer's
pipeline and consumer, not of a single document, and are assessed separately by
attestation and inspection.

Fixtures declare their expectation with '_test_expected_tier' ('compliant' or
null) and, where the failure is commerce-specific, '_test_expected_reason' as a
substring of one of the blocking reasons.

No external dependencies.

Usage:
    python3 validate.py
"""

import json
import sys
from pathlib import Path

CONTENT_EVENTS = {
    "content_retrieved",
    "content_grounded",
    "content_cited",
    "content_displayed",
    "content_engaged",
}
CITATION_CHAIN_EVENTS = {
    "content_grounded",
    "content_cited",
    "content_displayed",
}
VALID_TIERS = ("compliant",)


def is_standalone(doc):
    return doc.get("document_type") == "event"


def events(doc):
    """Yield the document's events, whether it is a session or standalone event."""
    if is_standalone(doc):
        event = doc.get("event")
        return [event] if event else []
    return doc.get("events", []) or []


def check_base_document(doc):
    """Document-level checks shared by Content Telemetry content events."""
    fails = []
    for i, event in enumerate(events(doc)):
        etype = event.get("type", "?")
        loc = f"event[{i}] {etype}"
        if "type" not in event:
            fails.append(f"{loc}: missing 'type'")
        if "timestamp" not in event:
            fails.append(f"{loc}: missing 'timestamp'")
        if (
            etype in CONTENT_EVENTS
            and not event.get("content_url")
            and not event.get("content_id")
        ):
            fails.append(f"{loc}: content event needs 'content_url' or 'content_id'")
        if etype == "content_retrieved" and not event.get("source_role"):
            fails.append(f"{loc}: content_retrieved missing 'source_role'")
    return fails


CLICK_OUT_ENGAGEMENTS = {"link_click", "agent_navigate"}


def click_out_events(doc):
    """Return (index, event) for every content_engaged click-out event
    (engagement_type link_click or agent_navigate, PROFILE.md section 3.5)."""
    out = []
    for i, event in enumerate(events(doc)):
        if event.get("type") == "content_engaged":
            data = event.get("data") or {}
            if data.get("engagement_type") in CLICK_OUT_ENGAGEMENTS:
                out.append((i, event))
    return out


def check_ctx_token(doc):
    """ctx_token propagation - PROFILE.md section 5.5.

    A cross-boundary click-out (link_click or agent_navigate) is one reported as
    a standalone event (how a destination or network reports a click-out). It
    MUST carry a ctx_token in place of session_id, and MUST NOT carry a raw
    session_id. A click-out that appears inside a full session document is the
    originating agent's own report and is not a cross-boundary event; we do not
    require ctx_token there, but if the fixture marks the flow as a commerce
    click-out we still expect the propagation path to be exercised by a
    ctx_token somewhere in the document.
    """
    fails = []
    clicks = click_out_events(doc)
    if is_standalone(doc):
        for i, event in clicks:
            etype = (event.get("data") or {}).get("engagement_type")
            loc = f"event[{i}] content_engaged {etype}"
            has_ctx = bool(doc.get("ctx_token"))
            has_session = bool(doc.get("session_id"))
            if not has_ctx:
                fails.append(
                    f"{loc}: cross-boundary click-out MUST carry 'ctx_token' "
                    f"(section 5.5)"
                )
            if has_session:
                fails.append(
                    f"{loc}: cross-boundary click-out MUST NOT carry raw "
                    f"'session_id' (section 5.5)"
                )
    return fails


def check_multi_citation(doc):
    """Multi-citation support - PROFILE.md section 5.6.

    A document that reports a click-out and claims to be a commerce flow MUST
    also carry the citation chain (grounded / cited / displayed) that a click
    manifest is built from. A standalone click-out event reported by a
    destination need not itself contain the chain - it references it by
    ctx_token - so this check applies to session documents that contain a
    click-out.
    """
    fails = []
    if is_standalone(doc):
        return fails
    clicks = click_out_events(doc)
    if not clicks:
        return fails
    chain_present = any(
        event.get("type") in CITATION_CHAIN_EVENTS for event in events(doc)
    )
    if not chain_present:
        fails.append(
            "session reports a click-out but carries no content_grounded, "
            "content_cited, or content_displayed events; no click manifest can "
            "be built (section 5.6)"
        )
    return fails


def assess(doc):
    """Return (tier or None, blocking reasons) for a document."""
    fails = check_base_document(doc) + check_ctx_token(doc) + check_multi_citation(doc)
    if not fails:
        return "compliant", []
    return None, fails


def main():
    fixtures_dir = Path(__file__).parent / "fixtures"
    if not fixtures_dir.is_dir():
        print(f"no fixtures directory at {fixtures_dir}", file=sys.stderr)
        return 1
    files = sorted(fixtures_dir.glob("*.json"))
    if not files:
        print(f"no fixtures found in {fixtures_dir}", file=sys.stderr)
        return 1

    print("OpenAttribution Commerce Profile - accreditation fixture suite\n")
    passed = failed = 0
    for path in files:
        try:
            doc = json.loads(path.read_text())
        except json.JSONDecodeError as exc:
            print(f"FAIL  {path.name}\n      invalid JSON: {exc}\n")
            failed += 1
            continue
        if "_test_expected_tier" not in doc:
            print(f"FAIL  {path.name}\n      fixture missing '_test_expected_tier'\n")
            failed += 1
            continue
        expected = doc["_test_expected_tier"]
        if expected is not None and expected not in VALID_TIERS:
            print(
                f"FAIL  {path.name}\n"
                f"      invalid '_test_expected_tier': {expected!r}\n"
            )
            failed += 1
            continue
        expected_reason = doc.get("_test_expected_reason")
        description = doc.get("_test_description", "")
        assessed, reasons = assess(doc)

        ok = assessed == expected
        if ok and expected is None and expected_reason:
            ok = any(expected_reason in r for r in reasons)

        if ok:
            passed += 1
            print(f"PASS  {path.name}")
            print(f"      {expected or 'no tier'} - {description}\n")
        else:
            failed += 1
            print(f"FAIL  {path.name}")
            print(
                f"      expected {expected or 'no tier'}, "
                f"assessed {assessed or 'no tier'}"
            )
            if expected_reason and expected is None:
                print(f"      expected a reason containing: {expected_reason!r}")
            if description:
                print(f"      {description}")
            if reasons:
                print("      blocked by:")
                for reason in reasons:
                    print(f"        - {reason}")
            elif expected is None and assessed is not None:
                print(f"      expected no tier, but the document qualifies for {assessed}")
            print()

    total = passed + failed
    print(f"{total} fixtures: {passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
