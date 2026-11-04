# ADR 0002: Slot-overflow scaling rule

Date: 2026-10-04
Status: accepted

## Context

The mark has 12 physical rings, but the collective will grow past 12 projects.
Re-tracing the artwork for a bigger mark is deferred.

## Decision

Treat the 12 rings as fixed reusable slots bound by the maintainer-controlled
`projectOrder` in `gitguild/src/project-curation.json`. Projects after the
first 12 are overflow: they remain accessible in the project browser and
through generated detail pages, but have no ring. Cross-highlighting only
applies to slotted projects.

## Consequences

- Adding a 13th repository is unblocked: refresh the snapshot or add it there,
  update curation if needed, then rebuild.
- A future bigger mark will be a re-trace with its own decision record.
- No separate all-projects index until search or filtering is clearly needed;
  the work section remains the index.
