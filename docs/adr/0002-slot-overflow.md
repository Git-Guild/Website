# ADR 0002: Slot-overflow scaling rule

Date: 2026-10-04
Status: accepted

## Context

The mark has 12 physical rings, but the collective will grow past 12 projects.
Re-tracing the artwork for a bigger mark is deferred.

## Decision

Treat the 12 rings as fixed reusable slots bound via `featured` and `order`:
slots are `order[:12]` (maintainers keep flagship/`featured` projects at the
front of `order`). Projects at `order[12:]` are overflow: they render as cards
plus dedicated pages with no ring, show a "card only" badge, and keep correct
counts. Cross-highlighting only applies to slotted projects.

## Consequences

- Adding a 13th project is unblocked: add it to `projects` and `order`, rebuild.
- A future bigger mark will be a re-trace with its own decision record.
- No separate all-projects index until search or filtering is clearly needed;
  the work section remains the index.
