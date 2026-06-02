#!/usr/bin/env python3
# FallMind · Stage 1 · export
# Walks Simon's local estate and emits green-rule training corpus.
# ◊·κ=1 · R0 ground · GREEN ONLY by default.

import argparse, hashlib, json, os, re, sys, time
from pathlib import Path

CC_PROJECTS_DIR = Path(r"C:\Users\sjgan\.claude\projects")
SI_DIDY_DIR     = Path(r"C:\Users\sjgan\Downloads\si-didy-agent")
DOWNLOADS_DIR   = Path(r"C:\Users\sjgan\Downloads")
ESTATE_GLOBS    = ("mesh-ripple", "fall-", "fallmind", "si-didy-agent")
OUT_DIR         = Path(__file__).resolve().parent.parent / "training-data"

RING_KEYWORDS = {
    "R0": ("intake","import","raw","ingest","input","upload","seed"),
    "R1": ("parse","extract","signal","feature","tokenize","split"),
    "R2": ("gate","validate","rule","exclude","filter","permission","auth"),
    "R3": ("ux","brand","design","palette","emotion","aesthetic","oxblood","brass"),
    "R4": ("build","render","ship","write","emit","compile","generate","forge"),
    "R5": ("verify","check","mirror","test","audit","assert","review"),
    "R6": ("watch","log","hash","audit chain","prevhash","cerebellum","omega"),
}

def ring_of(text: str) -> str:
    t = text.lower()
    best, score = "R4", 0
    for ring, kws in RING_KEYWORDS.items():
        s = sum(t.count(k) for k in kws)
        if s > score:
            score, best = s, ring
    return best

def h(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8", errors="ignore")).hexdigest()[:16]

def iter_jsonl(p: Path):
    try:
        with p.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line: continue
                try: yield json.loads(line)
                except Exception: continue
    except Exception: return

def extract_text(content) -> str:
    if isinstance(content, str): return content
    if isinstance(content, list):
        parts = []
        for c in content:
            if isinstance(c, dict):
                if c.get("type") == "text" and isinstance(c.get("text"), str):
                    parts.append(c["text"])
                elif isinstance(c.get("text"), str):
                    parts.append(c["text"])
        return "\n".join(parts)
    if isinstance(content, dict) and isinstance(content.get("text"), str):
        return content["text"]
    return ""

def walk_cc_sessions(seen):
    green, amber = [], []
    if not CC_PROJECTS_DIR.exists():
        print(f"[warn] CC dir missing: {CC_PROJECTS_DIR}", file=sys.stderr)
        return green, amber
    files = list(CC_PROJECTS_DIR.rglob("*.jsonl"))
    print(f"[scan] {len(files)} CC session files")
    for i, jf in enumerate(files):
        if i % 50 == 0 and i:
            print(f"  ... {i}/{len(files)}")
        for rec in iter_jsonl(jf):
            msg = rec.get("message") or rec
            role = msg.get("role") or rec.get("role") or rec.get("type")
            text = extract_text(msg.get("content") if isinstance(msg, dict) else None)
            if not text or len(text) < 8: continue
            if "[Request interrupted" in text: continue
            ts = rec.get("timestamp") or rec.get("ts") or ""
            entry = {
                "instruction": text.strip(),
                "source": f"cc-session:{jf.parent.name}/{jf.stem[:8]}",
                "ring": ring_of(text),
                "ts": ts,
            }
            key = h(entry["instruction"])
            if key in seen: continue
            seen.add(key)
            if role == "user":
                green.append(entry)
            elif role == "assistant":
                amber.append(entry)
    return green, amber

def walk_si_didy(seen):
    out = []
    if not SI_DIDY_DIR.exists(): return out
    for sub in ("memory", "missions"):
        d = SI_DIDY_DIR / sub
        if not d.exists(): continue
        for jf in d.rglob("*.jsonl"):
            for rec in iter_jsonl(jf):
                # Directive fields only — never agent responses.
                directive = (rec.get("directive") or rec.get("mission")
                             or rec.get("prompt") or rec.get("task") or "")
                if not isinstance(directive, str) or len(directive) < 8: continue
                key = h(directive)
                if key in seen: continue
                seen.add(key)
                out.append({
                    "instruction": directive.strip(),
                    "source": f"si-didy:{sub}/{jf.stem}",
                    "ring": ring_of(directive),
                    "ts": rec.get("ts") or rec.get("timestamp") or "",
                })
        # README + spec markdown inside si-didy
        for md in SI_DIDY_DIR.rglob("*.md"):
            try: txt = md.read_text(encoding="utf-8", errors="ignore")
            except Exception: continue
            if len(txt) < 64: continue
            key = h(txt[:512])
            if key in seen: continue
            seen.add(key)
            out.append({
                "instruction": f"Write the spec for {md.stem}",
                "response_seed": txt,
                "source": f"si-didy-spec:{md.relative_to(SI_DIDY_DIR).as_posix()}",
                "ring": ring_of(txt),
                "ts": "",
                "kind": "spec",
            })
    return out

def walk_estate_md(seen):
    out = []
    if not DOWNLOADS_DIR.exists(): return out
    for d in DOWNLOADS_DIR.iterdir():
        if not d.is_dir(): continue
        n = d.name.lower()
        if not any(g in n for g in ESTATE_GLOBS): continue
        for md in d.rglob("*.md"):
            if any(p in md.parts for p in ("node_modules",".git")): continue
            try: txt = md.read_text(encoding="utf-8", errors="ignore")
            except Exception: continue
            if len(txt) < 64: continue
            key = h(f"{d.name}:{md.name}:{txt[:512]}")
            if key in seen: continue
            seen.add(key)
            out.append({
                "instruction": f"Write the spec for {md.stem} ({d.name})",
                "response_seed": txt,
                "source": f"estate-spec:{d.name}/{md.relative_to(d).as_posix()}",
                "ring": ring_of(txt),
                "ts": "",
                "kind": "spec",
            })
    return out

def write_jsonl(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

def stats(rows, label):
    if not rows:
        print(f"[{label}] (empty)"); return
    rings = {}
    sources = {}
    total_bytes = 0
    for r in rows:
        rings[r["ring"]] = rings.get(r["ring"], 0) + 1
        src = r["source"].split(":")[0]
        sources[src] = sources.get(src, 0) + 1
        total_bytes += len(r.get("instruction","")) + len(r.get("response_seed","") or "")
    print(f"\n[{label}] rows={len(rows)} bytes={total_bytes:,}")
    print(f"  rings: {dict(sorted(rings.items()))}")
    print(f"  sources: {dict(sorted(sources.items(), key=lambda x:-x[1])[:8])}")

def main():
    ap = argparse.ArgumentParser(description="FallMind Stage-1 export · green-rule guarded")
    ap.add_argument("--include-amber", action="store_true",
                    help="DANGER: also emit assistant responses (ToS grey area)")
    ap.add_argument("--dry-run", action="store_true",
                    help="Scan + print stats but do not write JSONL")
    ap.add_argument("--out", default=str(OUT_DIR))
    args = ap.parse_args()

    if args.include_amber:
        print("\n" + "="*60)
        print("AMBER MODE ENGAGED")
        print("="*60)
        print("Assistant responses will be exported.")
        print("This is a ToS grey area for any frontier provider.")
        print("Default discipline is GREEN ONLY.")
        print("Type 'yes' to continue, anything else to abort:")
        if input("> ").strip().lower() != "yes":
            print("aborted."); return

    t0 = time.time()
    seen = set()
    print("[stage] CC sessions")
    cc_green, cc_amber = walk_cc_sessions(seen)
    print("[stage] si-didy memory/missions/specs")
    si = walk_si_didy(seen)
    print("[stage] estate markdown")
    estate = walk_estate_md(seen)

    green = cc_green + [r for r in si if r.get("kind") != "spec"]
    specs = [r for r in si if r.get("kind") == "spec"] + estate
    amber = cc_amber

    out = Path(args.out)
    stats(green, "GREEN prompts")
    stats(specs, "SPECS")
    stats(amber, "AMBER responses (locked unless --include-amber)")

    if not args.dry_run:
        write_jsonl(out / "simon-prompts.jsonl", green + specs)
        if args.include_amber:
            write_jsonl(out / "assistant-responses.jsonl", amber)
        print(f"\n[write] {out}/simon-prompts.jsonl  ({len(green)+len(specs)} rows)")
        if args.include_amber:
            print(f"[write] {out}/assistant-responses.jsonl  ({len(amber)} rows)")
    else:
        print("\n[dry-run] no files written.")

    print(f"\n[done] {time.time()-t0:.1f}s")

if __name__ == "__main__":
    main()
