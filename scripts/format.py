#!/usr/bin/env python3
# FallMind · Stage 2 · format
# Read simon-prompts.jsonl + specs · produce LoRA-ready instruction/response pairs.
# ◊·κ=1 · R4 voice render

import argparse, json, re, sys
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "training-data"

STOP = set("the a an and or but if then so to of in on at for with as is are was were be been being it its this that these those i you we they them us our your".split())

def tokens(s: str):
    return [w for w in re.findall(r"[a-z0-9\-]{3,}", s.lower()) if w not in STOP]

def best_spec(prompt: str, specs: list[dict]) -> dict | None:
    p_tok = set(tokens(prompt))
    if not p_tok or not specs: return None
    best, bs = None, 0
    for s in specs:
        s_tok = set(tokens(s.get("response_seed","")[:2000]) + tokens(s.get("source","")))
        if not s_tok: continue
        overlap = len(p_tok & s_tok)
        if overlap > bs:
            bs, best = overlap, s
    return best if bs >= 3 else None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="src", default=str(DATA / "simon-prompts.jsonl"))
    ap.add_argument("--out", default=str(DATA / "lora-ready.jsonl"))
    ap.add_argument("--max-len", type=int, default=8192)
    args = ap.parse_args()

    src = Path(args.src)
    if not src.exists():
        print(f"[err] missing {src} · run scripts/export.py first", file=sys.stderr)
        sys.exit(1)

    rows = [json.loads(l) for l in src.read_text(encoding="utf-8").splitlines() if l.strip()]
    specs   = [r for r in rows if r.get("kind") == "spec"]
    prompts = [r for r in rows if r.get("kind") != "spec"]
    print(f"[load] {len(prompts)} prompts · {len(specs)} specs")

    pairs = []
    # Spec self-pairs (the safe pattern: instruction = "write the spec for X", response = spec body)
    for s in specs:
        body = (s.get("response_seed") or "")[:args.max_len]
        if not body: continue
        pairs.append({
            "instruction": s["instruction"],
            "response":    body,
            "ring":        s.get("ring","R4"),
            "source":      s.get("source",""),
            "ts":          s.get("ts",""),
            "pair_kind":   "spec-self",
        })

    # Prompt pairs (prompt -> closest spec, if we can find one)
    for p in prompts:
        match = best_spec(p["instruction"], specs)
        resp  = (match.get("response_seed","")[:args.max_len] if match
                 else "[no matched spec · use base-model fallback during SFT]")
        pairs.append({
            "instruction": p["instruction"][:args.max_len],
            "response":    resp,
            "ring":        p.get("ring","R4"),
            "source":      p.get("source",""),
            "ts":          p.get("ts",""),
            "pair_kind":   "prompt-spec" if match else "prompt-orphan",
            "matched":     match.get("source") if match else None,
        })

    # Write
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for r in pairs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Stats
    rings = Counter(r["ring"] for r in pairs)
    kinds = Counter(r["pair_kind"] for r in pairs)
    avg_len = sum(len(r["instruction"]) + len(r["response"]) for r in pairs) // max(len(pairs),1)
    print(f"\n[done] pairs={len(pairs)}")
    print(f"  rings: {dict(sorted(rings.items()))}")
    print(f"  kinds: {dict(kinds)}")
    print(f"  avg length: {avg_len} chars")
    print(f"  out: {out}")

if __name__ == "__main__":
    main()
