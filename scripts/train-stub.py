#!/usr/bin/env python3
# FallMind · Stage 3 · LoRA training runner (Unsloth)
# ◊·κ=1 · GPU REQUIRED · this file is intentionally inert without CUDA.

import argparse, os, sys

BANNER = """
================================================================
  FallMind · Stage 3 · Unsloth LoRA SFT runner
  ◊ · κ = 1 · v20 mastery seal · 7-ring discipline
================================================================
"""

def main():
    ap = argparse.ArgumentParser(description="FallMind LoRA training (Unsloth)")
    ap.add_argument("--base-model",     default="meta-llama/Llama-3.1-8B-Instruct")
    ap.add_argument("--training-data",  default="./training-data/lora-ready.jsonl")
    ap.add_argument("--output",         default="./simon-lora")
    ap.add_argument("--epochs",         type=int,   default=3)
    ap.add_argument("--lora-rank",      type=int,   default=32)
    ap.add_argument("--lora-alpha",     type=int,   default=64)
    ap.add_argument("--learning-rate",  type=float, default=2e-4)
    ap.add_argument("--max-seq-length", type=int,   default=4096)
    ap.add_argument("--batch-size",     type=int,   default=2)
    ap.add_argument("--grad-accum",     type=int,   default=4)
    args = ap.parse_args()

    print(BANNER)
    print(f"  base-model     : {args.base_model}")
    print(f"  training-data  : {args.training_data}")
    print(f"  output         : {args.output}")
    print(f"  epochs         : {args.epochs}")
    print(f"  lora-rank      : {args.lora_rank}")
    print(f"  lora-alpha     : {args.lora_alpha}")
    print(f"  learning-rate  : {args.learning_rate}")
    print(f"  max-seq-length : {args.max_seq_length}")
    print()

    try:
        import torch
        if not torch.cuda.is_available():
            print("GPU REQUIRED · this script is the runner.")
            print("Execute on RTX 4090+ or café session with CUDA.")
            print("Aborting harmlessly (no GPU detected).")
            sys.exit(0)
    except ImportError:
        print("torch not installed · install unsloth bundle before running.")
        print("  pip install \"unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git\"")
        sys.exit(0)

    # --- Real path begins here · only executed on GPU box ---
    from unsloth import FastLanguageModel
    from datasets import load_dataset
    from trl import SFTTrainer
    from transformers import TrainingArguments

    model, tok = FastLanguageModel.from_pretrained(
        model_name = args.base_model,
        max_seq_length = args.max_seq_length,
        load_in_4bit = True,
    )
    model = FastLanguageModel.get_peft_model(
        model,
        r = args.lora_rank,
        lora_alpha = args.lora_alpha,
        target_modules = ["q_proj","k_proj","v_proj","o_proj",
                          "gate_proj","up_proj","down_proj"],
        bias = "none",
        use_gradient_checkpointing = "unsloth",
    )

    def fmt(ex):
        return {"text": (
            f"### Instruction:\n{ex['instruction']}\n\n"
            f"### Response:\n{ex['response']}"
        )}
    ds = load_dataset("json", data_files=args.training_data, split="train").map(fmt)

    trainer = SFTTrainer(
        model = model, tokenizer = tok, train_dataset = ds,
        dataset_text_field = "text", max_seq_length = args.max_seq_length,
        args = TrainingArguments(
            per_device_train_batch_size = args.batch_size,
            gradient_accumulation_steps = args.grad_accum,
            num_train_epochs = args.epochs,
            learning_rate = args.learning_rate,
            warmup_steps = 10, logging_steps = 5,
            output_dir = args.output, save_strategy = "epoch",
            optim = "adamw_8bit", lr_scheduler_type = "cosine",
            bf16 = True, report_to = "none",
        ),
    )
    trainer.train()
    model.save_pretrained(args.output)
    tok.save_pretrained(args.output)
    print(f"\n[done] LoRA adapter written to {args.output}")
    print("[next] scripts/merge.py --adapter " + args.output)

if __name__ == "__main__":
    main()
