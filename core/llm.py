# -*- coding: utf-8 -*-
"""OpenAI 兼容大模型客户端（DeepSeek/通义/Moonshot/OpenAI 等）。
配置读取项目根目录 .env：LLM_API_KEY / LLM_BASE_URL / LLM_MODEL。"""
import json
import os
import re
import urllib.request
from pathlib import Path

_BASE = Path(__file__).resolve().parent.parent


def load_env():
    p = _BASE / ".env"
    if p.exists():
        for raw in p.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


load_env()


def get(key, default=None):
    return os.environ.get(key, default)


def is_configured():
    return bool(get("LLM_API_KEY"))


def provider_label():
    base = (get("LLM_BASE_URL", "") or "")
    if "deepseek" in base:
        return "DeepSeek"
    if "moonshot" in base:
        return "Moonshot"
    if "dashscope" in base or "aliyun" in base:
        return "通义千问"
    if "openai" in base:
        return "OpenAI"
    return "大模型"


def chat(messages, temperature=0.7, max_tokens=1200, timeout=60):
    base = (get("LLM_BASE_URL") or "https://api.deepseek.com/v1").rstrip("/")
    url = base + "/chat/completions"
    payload = {
        "model": get("LLM_MODEL") or "deepseek-chat",
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json",
                 "Authorization": "Bearer " + (get("LLM_API_KEY") or "")},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return (data["choices"][0]["message"]["content"] or "").strip()


def parse_json(text):
    """尝试从模型输出中解析 JSON（容忍 ```json 包裹或前后杂文）。"""
    if not text:
        return None
    t = text.strip()
    if t.startswith("```"):
        t = re.sub(r"^```[a-zA-Z]*\s*", "", t)
        t = re.sub(r"\s*```$", "", t).strip()
    try:
        return json.loads(t)
    except Exception:
        pass
    for start, end in (("{", "}"), ("[", "]")):
        i = t.find(start)
        if i >= 0:
            j = t.rfind(end)
            if j > i:
                try:
                    return json.loads(t[i:j + 1])
                except Exception:
                    pass
    return None