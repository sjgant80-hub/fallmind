# FallMind mesh router — design note

Scope: the routing layer in `mesh/router.js`. This note fixes the observable
contract of that module so a change in behaviour is a change against a written
spec, not a surprise. It documents only what the code does today; the training
pipeline (`scripts/`) and the dashboard (`fallmind.html`) are out of scope here.

Status: accepted, describes shipped behaviour as of package version 0.1.0.

## 1. Purpose

`mesh/router.js` is a pure, dependency-free ES module that decides which model
in a small mesh should answer a query, and at what escalation tier. It is a
scaffold: some members have no live endpoint yet, so the router is written to
degrade to the always-local member rather than to fail. All of its exported
functions are deterministic and side-effect-free except `broadcastPresence`.

## 2. The mesh table

`MESH_MODELS` is a fixed record of three members, keyed by name:

| key              | member   | serves tiers      | endpoint            | cost  |
| ---------------- | -------- | ----------------- | ------------------- | ----- |
| `simon-mind`     | `simon`  | T0, T1, T2        | loopback (Ollama)   | 0     |
| `thomas-mind`    | `thomas` | T2, T3            | `null` (not wired)  | 0     |
| `estate-cascade` | `estate` | T2.5, T3          | remote cascade      | 0.001 |

Each member carries a 7-element `bloom` vector used as its routing feature
vector. `simon-mind` is the only member reachable at the two lowest tiers and is
the universal fallback. `FALLMIND_PRIME` is exported as the constant `587`.

## 3. Routing feature vector (`bloom`)

A `bloom` is a length-7 histogram over seven keyword buckets, R0..R6. Each
bucket holds a small keyword set (`RING_KW` in the source). `queryBloom(text)`
lowercases the text and, for each bucket, counts total keyword occurrences
(global, overlapping-substring count via `RegExp`). Contract:

- Input `""`, `null`, or `undefined` returns `[0,0,0,0,0,0,0]`.
- The vector index equals the bucket number: R0 is index 0 ... R6 is index 6.
- Buckets are independent; a query touching only R4 keywords leaves the other
  six indices at zero.

## 4. Similarity (`bloomSimilarity`)

Cosine similarity of two equal-length numeric vectors. Contract:

- Identical direction returns cosine `1` up to floating-point error. Note: for a
  vector against an exact copy the result is `0.9999999999999999`, i.e. strictly
  below `1` — callers must compare with a tolerance, never `=== 1`.
- Scale-invariant: `v` against `k·v` returns exactly `1`.
- Returns `0` for: a missing operand, a length mismatch, or a zero-magnitude
  vector (the denominator guard prevents divide-by-zero). Never throws.

## 5. Tier ladder (`pickTier`)

Maps a confidence in `[0,1]` to an escalation tier. Confidence defaults to
`1.0`. Boundaries are inclusive at the lower edge:

| confidence ≥ | tier |
| ------------ | ---- |
| 0.85         | T0   |
| 0.70         | T1   |
| 0.55         | T2   |
| 0.40         | T2.5 |
| (below 0.40) | T3   |

## 6. Selection (`routeQuery`)

Given a query string and a tier (default `T0`), `routeQuery`:

1. Computes the query bloom and scores every member that serves the tier by
   cosine similarity against the member's bloom.
2. Sorts by score, descending.
3. Applies the **no-endpoint fallback rule**: if no member serves the tier, or
   the top-scoring member has a `null` endpoint, it logs the intended decision
   and returns `simon-mind`.
4. Otherwise returns the top-scoring member.

The fallback rule has a deliberately non-obvious consequence at T2: `thomas-mind`
can out-score `simon-mind` yet still be skipped because its endpoint is not wired,
so T2 resolves to `simon-mind`. This is verified in `test.mjs`.

`routeQuery` always returns one of the `MESH_MODELS` objects — never `null`.

## 7. Presence (`broadcastPresence`)

The one impure export. It posts a presence message on the `fall-signal`
`BroadcastChannel` and returns `undefined`. It must never throw in a host that
lacks `BroadcastChannel`; where the channel exists it is opened, which keeps the
event loop alive, so a batch runner that calls it should exit explicitly.

## 8. Testable surface

The router is the honestly unit-testable part of this repository (the pipeline
scripts require a GPU and the HTML is a DOM app). `test.mjs` imports the module
and asserts the contract above against real recorded outputs, including the
floating-point cosine, the tier boundaries, and the no-endpoint fallback. Run it
with `node test.mjs` or `npm test`.
