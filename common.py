"""Zhipu GLM-4 共用调用层。直接走 requests，不依赖 zhipuai SDK。"""
import os, json, requests

ROOT = os.path.dirname(os.path.abspath(__file__))
ENV_CANDIDATES = [
    os.path.join(ROOT, ".env"),
    os.path.join(ROOT, "..", "agent-tool-loop-lab", ".env"),
]

def _load_env():
    cfg = {}
    for path in ENV_CANDIDATES:
        if not os.path.exists(path):
            continue
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line and "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                cfg[k.strip()] = v.strip()
        if cfg.get("ZHIPU_API_KEY"):
            break
    return cfg

CFG = _load_env()
API_KEY  = CFG.get("ZHIPU_API_KEY", "")
BASE_URL = CFG.get("ZHIPU_BASE_URL", "https://open.bigmodel.cn/api/paas/v4")
MODEL    = CFG.get("ZHIPU_MODEL", "glm-4-flash")

def chat(messages, model=None, temperature=0.7, tools=None):
    """OpenAI 兼容的 chat completions。返回原始 JSON。"""
    url = f"{BASE_URL}/chat/completions"
    body = {
        "model": model or MODEL,
        "messages": messages,
        "temperature": temperature,
    }
    if tools:
        body["tools"] = tools
    r = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json=body, timeout=120,
    )
    r.raise_for_status()
    return r.json()

def chat_text(messages, **kw):
    """只取 content 文本。"""
    j = chat(messages, **kw)
    return j["choices"][0]["message"].get("content", "") or ""
