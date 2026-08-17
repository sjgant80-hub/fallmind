# CLAUDE.md — working notes for agents in this repo

FallMind trains a small local LLM on the maintainer's own prompts/specs and
routes queries across a tiny model mesh. Keep changes small and reviewable.

## Layout

- `mesh/router.js` — pure, zero-dependency ES module. The routing contract is
  fixed in `SPEC.md`. This is the unit-tested core.
- `scripts/*.py` — the training pipeline (export → format → train → merge →
  ollama). Stages 3–5 need a CUDA GPU and cannot run on this machine.
- `fallmind.html`, `index.html` — the browser dashboard.
- `test.mjs` — the suite for `mesh/router.js`. Run with `npm test`.

## Rules for changes

- Treat `SPEC.md` as the source of truth for `mesh/router.js`. If you change the
  module's observable behaviour, update `SPEC.md` and `test.mjs` in the same
  change, and bump the package version.
- The router must stay dependency-free and deterministic (except
  `broadcastPresence`). No network calls, no new runtime dependencies.
- Preserve the no-endpoint fallback rule: any member with a `null` endpoint is
  skipped in favour of `simon-mind`. Tests depend on this.
- `broadcastPresence` must never throw when `BroadcastChannel` is absent.

## Testing

- `npm test` runs `node test.mjs`. Every assertion is derived from real recorded
  output; do not weaken an assertion to make the suite pass — fix the code or
  update the spec.
- The suite calls `process.exit` on purpose: `broadcastPresence` opens a
  `BroadcastChannel` that would otherwise keep the process alive.

## Green-rule reminder

The export pipeline emits only the maintainer's own prompts and specs by
default. Do not change that default without an explicit, documented decision.
