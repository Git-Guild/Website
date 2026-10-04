# ADR 0001: React UMD interim (no new pipeline)

Date: 2026-10-04
Status: accepted

## Context

The home page needs component-style rendering for the emblem, cards, merge
train, and panel, but the repo rule is Python-only assembly with offline static
deploy: no package manager, bundler, or hosted build step.

## Decision

Render with React loaded as an inlined UMD runtime. The assembler inlines
`react.production.min.js` plus `react-dom.production.min.js` and the
application script (written with `React.createElement`, no JSX tooling) into
the home payload. No CDN at runtime, no external requests.

## Consequences

- Home stays a single self-contained file; deploy remains drag-drop.
- App code uses `React.createElement` so no build tooling is needed.
- If React UMD is ever dropped by upstream, vendor the files (already done
  under `tools/build/`) and revisit; a future Vite plus Tailwind migration is
  explicitly out of scope.
