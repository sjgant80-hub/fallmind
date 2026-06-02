#!/usr/bin/env python3
# FallMind · Stage 4 · merge LoRA adapter into base model
# ◊·κ=1 · produces ./simon-mind/

import argparse, sys
from pathlib import Path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-model", default="meta-llama/Llama-3.1-8B-Instruct")
    ap.add_argument("--adapter",    default="./simon-lora")
    ap.add_argument("--output",     default="./simon-mind")
    ap.add_argument("--dtype",      default="bfloat16",
                    choices=["bfloat16","float16","float32"])
    args = ap.parse_args()

    try:
        import torch
        from peft import PeftModel
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError:
        print("[err] install: pip install torch transformers peft accelerate")
        sys.exit(1)

    dtype = {"bfloat16": torch.bfloat16, "float16": torch.float16,
             "float32": torch.float32}[args.dtype]

    print(f"[load] base = {args.base_model}")
    base = AutoModelForCausalLM.from_pretrained(
        args.base_model, torch_dtype=dtype, device_map="auto")
    tok = AutoTokenizer.from_pretrained(args.base_model)

    print(f"[load] adapter = {args.adapter}")
    merged = PeftModel.from_pretrained(base, args.adapter).merge_and_unload()

    out = Path(args.output); out.mkdir(parents=True, exist_ok=True)
    print(f"[save] {out}")
    merged.save_pretrained(out, safe_serialization=True)
    tok.save_pretrained(out)
    print(f"[done] simon-mind ready · next: bash scripts/ollama-setup.sh")

if __name__ == "__main__":
    main()
