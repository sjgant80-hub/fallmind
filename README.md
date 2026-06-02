# FallMind &middot; sovereign self-trained LLM

> Train a language model on Simon's own prompts and specs. Run it on Simon's own hardware. Plug into the estate cascade and the guild mesh. No cloud. No leash.
>
> ◊ &middot; &kappa; = 1 &middot; prime 587 &middot; ring focus R4 (build) + R6 (watcher) &middot; v20 mastery seal

| | |
| --- | --- |
| **Live** | https://sjgant80-hub.github.io/fallmind/ |
| **Prime** | 587 (the 107th prime &middot; FallReach is prime 107 &middot; FallMind is its cognitive sibling) |
| **Rings** | R4 voice (the build) &middot; R6 watcher (the model audits its own training) |
| **Bloom** | [4,7,7,6,5,4,3] &middot; Simon's mountain shape |
| **Licence** | MIT |
| **Mesh** | fall-signal BroadcastChannel + bloom router scaffold |

---

## For the end user

### What FallMind is

A pipeline that takes Simon's accumulated conversational and architectural output
&mdash; the prompts he wrote into Claude Code, the specs he committed to the estate &mdash;
and trains a small language model that thinks the way Simon thinks. The model
runs locally on Simon's machine via Ollama. The estate cascade calls it first
before reaching for any frontier API.

This is a sovereignty play. Three reasons:

1. The voice is Simon's. The estate's character should not depend on a frontier provider's roadmap.
2. The data never leaves the box. Green-rule discipline: only Simon's own prompts and his own specs are exported. No assistant responses by default.
3. The cascade gets faster and cheaper as the local model gets better. The frontier API becomes the last resort, not the first.

### What runs today vs. what needs a GPU

| stage | name | runs now? |
| --- | --- | --- |
| 1 | `scripts/export.py` &middot; walk CC sessions + estate specs &middot; emit JSONL | yes |
| 2 | `scripts/format.py` &middot; LoRA-ready instruction/response pairs | yes |
| 3 | `scripts/train-stub.py` &middot; Unsloth LoRA SFT on Llama-3.1-8B | needs RTX 4090+ |
| 4 | `scripts/merge.py` &middot; merge adapter, produce `./simon-mind` | needs CUDA |
| 5 | `scripts/ollama-setup.sh` &middot; register `simon-mind`, pull 70B fallback | needs Ollama + disk |
| 6 | `mesh/router.js` &middot; bloom-routed cascade across simon-mind / thomas-mind / estate | yes (scaffold) |
| 7 | `fallmind.html` &middot; the visible piece &middot; stats + status + cascade view | yes |

Stages 1, 2, 6, 7 ship and work today. Stages 3, 4, 5 are wired and ready but
need a CUDA box.

### How to install (end user path)

```
git clone https://github.com/sjgant80-hub/fallmind
cd fallmind
python scripts/export.py            # emits training-data/simon-prompts.jsonl
python scripts/format.py            # emits training-data/lora-ready.jsonl
# Open fallmind.html in a browser. Done. The page reads the JSONL and shows stats.

# When GPU arrives:
python scripts/train-stub.py --base-model meta-llama/Llama-3.1-8B-Instruct
python scripts/merge.py
bash   scripts/ollama-setup.sh
# Reload fallmind.html. The Ollama panel now sees simon-mind.
```

### Sovereignty timeline

| year | what happens |
| --- | --- |
| Y1 &middot; now | Export green corpus. Format LoRA pairs. Ship the scaffold. Wait for GPU. |
| Y1 &middot; q3 | First LoRA on Llama-3.1-8B. Merge into `simon-mind`. Register in Ollama. Cascade T0 = self. |
| Y2 | Continual SFT on every new estate prompt. Bloom drift monitored by R5 mirror. |
| Y3 | Mesh: simon-mind + thomas-mind handshake. Bloom-routed delegation. Real WebRTC. |
| Y4+ | Guild constellation. Frontier-class capability without frontier dependence. v21 never happens &mdash; runewords on v20. |

---

## For the developer

### Pipeline architecture

```
                                          GREEN PATH ONLY (default)
  +------------------+        +----------+      +----------+      +----------+
  | CC session JSONL |  -->   | export   | -->  | format   | -->  | LoRA     |
  | si-didy memory   |        | (R0)     |      | (R4)     |      | training |
  | estate .md specs |        +----+-----+      +----+-----+      +----+-----+
  +------------------+             |                 |                 |
                                   v                 v                 v
                          simon-prompts.jsonl   lora-ready.jsonl   simon-lora/
                                                                       |
                                                                       v
                                                                   merge.py
                                                                       |
                                                                       v
                                                                 ./simon-mind/
                                                                       |
                                                                       v
                                                              ollama create  ->  T0 ready
```

The cascade then looks like this:

```
  query  ->  T0 simon-mind          (local LoRA · first responder)
         ->  T1 llama3.1:8b          (local fallback)
         ->  T2 mesh peer            (thomas-mind via WebRTC · future)
         ->  T2.5 llama3.1:70b-q4    (local heavy)
         ->  T3 frontier API         (last resort · rare)
```

### Green-rule guard

The export script never emits assistant/Claude response text by default. The
`--include-amber` flag exists to support the rare case where a user knowingly
wants to include assistant output, but defaults to FALSE and prints a 5-line
warning + interactive confirmation when used. This is deliberate. Frontier
provider ToS are ambiguous on assistant-response reuse for training; we stay
clearly inside the safe zone.

### File map

```
fallmind/
  fallmind.html               # the sovereign single-file dashboard
  Modelfile.template          # Ollama Modelfile with v20 SYSTEM block
  scripts/
    export.py                 # stage 1 · walk + emit green corpus
    format.py                 # stage 2 · LoRA-ready pairs
    train-stub.py             # stage 3 · Unsloth runner (GPU required)
    merge.py                  # stage 4 · merge LoRA into base
    ollama-setup.sh           # stage 5 · register + pull 70B
  mesh/
    router.js                 # bloom-routed cascade scaffold
  training-data/              # gitignored · created by export.py
    simon-prompts.jsonl
    lora-ready.jsonl
    assistant-responses.jsonl # only if --include-amber
  README.md
  LICENSE
  .nojekyll
  package.json
```

### How each script works

**export.py** &middot; walks three sources:

- `C:\Users\sjgan\.claude\projects\` recursively for all `*.jsonl` &mdash; extracts only user-role messages.
- `C:\Users\sjgan\Downloads\si-didy-agent\memory\` and `missions\` &mdash; pulls directive fields only.
- `C:\Users\sjgan\Downloads\{mesh-ripple, fall-*, si-didy-agent}\**\*.md` &mdash; pulls full spec content.

Output schema:

```json
{"instruction":"...","source":"cc-session:repo/abcd1234","ring":"R4","ts":"..."}
```

Stats printed: total prompts, total specs, total bytes, source breakdown, ring distribution.

**format.py** &middot; reads `simon-prompts.jsonl` and synthesises LoRA training pairs:

- For each spec: emit `(instruction = "Write the spec for X", response = spec body)` &mdash; the safe pattern.
- For each prompt: pair with the closest spec by keyword overlap; orphan prompts become base-model fallback pairs.
- Adds ring tag, source tag, timestamp, pair_kind.

**train-stub.py** &middot; full Unsloth boilerplate. Prints `GPU REQUIRED` and exits cleanly if no CUDA. When CUDA is present, runs SFT and writes `./simon-lora`.

**merge.py** &middot; loads base + LoRA, calls `merge_and_unload()`, writes `./simon-mind` in safetensors.

**ollama-setup.sh** &middot; copies the Modelfile template, runs `ollama create simon-mind`, smoke-tests, then `ollama pull llama3.1:70b-instruct-q4_K_M` for T2.5.

**mesh/router.js** &middot; ESM module. Exports `routeQuery(text, tier)` and `bloomSimilarity(a,b)`. Console-logs the would-be routing decision for any tier whose endpoint is not yet wired.

### How it composes into the estate cascade

FallMind sits inside the estate at prime 587. It broadcasts presence on `fall-signal`. Any other estate tool that wants Simon-voice output can route through the cascade defined in `mesh/router.js`. FallCore (the local-LLM proxy) is the T2 fall-through. The frontier API is T3 and rarely needed once T0 is warm.

### Honest constraints (verbatim from spec)

- No GPU on this machine. Stages 3-5 are wired but cannot run here.
- Konomi cert mint is **pending** &mdash; no `./konomi.key` Ed25519 sourced yet (v2.1 audit note). Konomi shim runs in sovereign tier (no gate).
- Mesh real WebRTC handshake stubs out to a `console.log` until the first peer answers. The bloom-similarity routing logic itself is real and correct.
- Spec-to-prompt pairing in `format.py` is keyword overlap, not semantic. Good enough for an SFT seed; not a retrieval system.
- No npm install of heavy dependencies. Vanilla JS for `fallmind.html`. Python stdlib + Unsloth-only for scripts.

### Links

- Plugin registry: [sjgant80-hub/fall-registry](https://github.com/sjgant80-hub/fall-registry)
- Estate browser: [FallCompass](https://sjgant80-hub.github.io/fallcompass/)
- Agent harness: [si-didy-agent](https://github.com/sjgant80-hub/si-didy-agent)
- FallCore (T2 proxy): [sjgant80-hub/fallcore](https://github.com/sjgant80-hub/fallcore)

### Licence

MIT &middot; see `LICENSE`.
