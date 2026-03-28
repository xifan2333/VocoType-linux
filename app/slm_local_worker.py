#!/usr/bin/env python3
"""Ephemeral local SLM worker.

Protocol (JSON lines over stdio):
- startup: emit {"type":"ready","ok":true}
- request: {"type":"polish", ...}
- response: {"ok":true,"text":"..."} or {"ok":false,"reason":"..."}
- exit: {"type":"exit"}
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from typing import Any, Dict

THINKING_PREFIX_RE = re.compile(
    r"^\s*(?:thinking\s*process|thought\s*process|reasoning|analysis|chain\s*of\s*thought|思考过程|推理过程|分析过程)\s*[:：]",
    flags=re.IGNORECASE,
)
FINAL_ANSWER_MARKER_RE = re.compile(
    r"(?:(?:^|\n)\s*)(?:final\s*answer|final\s*response|answer|最终答案|最终输出|润色结果|输出结果|输出)\s*[:：]",
    flags=re.IGNORECASE,
)
REASONING_LINE_RE = re.compile(
    r"^\s*(?:"
    r"(?:thinking\s*process|thought\s*process|reasoning|analysis|chain\s*of\s*thought|let'?s\s+think|step\s*\d*)"
    r"|(?:思考过程|推理过程|分析过程|推理|分析|思路)"
    r"|(?:\d+[\.\)]\s+)"
    r"|(?:[-*]\s+)"
    r")",
    flags=re.IGNORECASE,
)


def emit(payload: Dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def clamp_float(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


@dataclass
class Runtime:
    tokenizer: Any
    model: Any
    torch: Any
    device: str


def load_runtime(model_name: str, device: str, dtype: str) -> Runtime:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)

    torch_dtype = None
    if dtype == "float16":
        torch_dtype = torch.float16
    elif dtype == "bfloat16":
        torch_dtype = torch.bfloat16
    elif dtype == "float32":
        torch_dtype = torch.float32

    model_kwargs: Dict[str, Any] = {
        "trust_remote_code": True,
    }
    if torch_dtype is not None:
        model_kwargs["torch_dtype"] = torch_dtype

    model = AutoModelForCausalLM.from_pretrained(model_name, **model_kwargs)

    if device != "cpu":
        model.to(device)

    model.eval()
    return Runtime(tokenizer=tokenizer, model=model, torch=torch, device=device)


def build_prompt(
    tokenizer: Any,
    system_prompt: str,
    text: str,
    *,
    enable_thinking: bool,
) -> str:
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"原文：{text}\n输出："},
    ]

    apply_chat_template = getattr(tokenizer, "apply_chat_template", None)
    if callable(apply_chat_template):
        try:
            return tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=enable_thinking,
            )
        except TypeError:
            return tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )

    return f"{system_prompt}\n\n原文：{text}\n输出："


def run_polish(runtime: Runtime, request: Dict[str, Any]) -> Dict[str, Any]:
    text = str(request.get("text", "")).strip()
    if not text:
        return {"ok": False, "reason": "empty_text"}

    system_prompt = str(request.get("system_prompt", "")).strip()
    if not system_prompt:
        return {"ok": False, "reason": "empty_system_prompt"}

    max_tokens = max(1, int(request.get("max_tokens", 24)))
    temperature = float(request.get("temperature", 0.2))
    top_p = float(request.get("top_p", 0.9))
    enable_thinking = bool(request.get("enable_thinking", False))

    prompt = build_prompt(
        runtime.tokenizer,
        system_prompt,
        text,
        enable_thinking=enable_thinking,
    )
    encoded = runtime.tokenizer(prompt, return_tensors="pt")

    if runtime.device != "cpu":
        encoded = {k: v.to(runtime.device) for k, v in encoded.items()}

    do_sample = temperature > 0.0
    gen_kwargs: Dict[str, Any] = {
        "max_new_tokens": max_tokens,
        "do_sample": do_sample,
    }
    if do_sample:
        gen_kwargs["temperature"] = clamp_float(temperature, 1e-5, 2.0)
        gen_kwargs["top_p"] = clamp_float(top_p, 0.01, 1.0)

    with runtime.torch.no_grad():
        output_ids = runtime.model.generate(**encoded, **gen_kwargs)

    input_len = int(encoded["input_ids"].shape[1])
    generated_ids = output_ids[0][input_len:]
    content = runtime.tokenizer.decode(generated_ids, skip_special_tokens=True).strip()
    content = strip_thinking_content(content)
    if not content:
        return {"ok": False, "reason": "thinking_only"}

    return {"ok": True, "text": content}


def strip_thinking_content(content: str) -> str:
    text = str(content or "")
    if not text:
        return ""

    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    if "<think>" in text:
        text = text.split("<think>", 1)[0]
    text = text.strip()
    if not text:
        return ""

    marker_matches = list(FINAL_ANSWER_MARKER_RE.finditer(text))
    if marker_matches:
        candidate = text[marker_matches[-1].end() :].strip()
        if candidate:
            text = candidate
        else:
            return ""

    if not THINKING_PREFIX_RE.match(text):
        return text

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n+", text) if p.strip()]
    if len(paragraphs) >= 2:
        last_para = paragraphs[-1]
        if not is_reasoning_line(last_para):
            return last_para

    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    for line in reversed(lines):
        if is_reasoning_line(line):
            continue
        return line
    return ""


def is_reasoning_line(text: str) -> bool:
    return bool(REASONING_LINE_RE.match(str(text or "").strip()))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="VoCoType local SLM worker")
    parser.add_argument("--model", required=True, help="HuggingFace model id or local path")
    parser.add_argument(
        "--device",
        default="cpu",
        help="torch device, e.g. cpu / cuda:0",
    )
    parser.add_argument(
        "--dtype",
        default="auto",
        choices=["auto", "float16", "bfloat16", "float32"],
        help="model dtype hint",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        runtime = load_runtime(args.model, args.device, args.dtype)
        emit({"type": "ready", "ok": True})
    except Exception as exc:  # noqa: BLE001
        emit({"type": "ready", "ok": False, "reason": f"load_failed:{exc}"})
        return 1

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            emit({"ok": False, "reason": "bad_request_json"})
            continue

        req_type = req.get("type")
        if req_type == "exit":
            emit({"ok": True})
            return 0
        if req_type != "polish":
            emit({"ok": False, "reason": "unknown_request_type"})
            continue

        try:
            emit(run_polish(runtime, req))
        except Exception as exc:  # noqa: BLE001
            emit({"ok": False, "reason": f"infer_failed:{exc}"})

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
