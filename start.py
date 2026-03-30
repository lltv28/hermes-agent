import json, os
from pathlib import Path

h = Path(os.environ.get("HERMES_HOME", "/app/.hermes"))
h.mkdir(parents=True, exist_ok=True)

# --- config.yaml: MiniMax M2.7 primary, OpenRouter fallback ---
c = h / "config.yaml"
import yaml

cfg = {}
if c.exists():
    try:
        cfg = yaml.safe_load(c.read_text()) or {}
    except Exception:
        cfg = {}

# Primary: MiniMax M2.7 via Anthropic-compatible endpoint
cfg["model"] = {
    "default": "MiniMax-M2.7-highspeed",
    "provider": "minimax",
    "base_url": "https://api.minimax.io/anthropic",
}

# Fallback chain: Gemini Flash on OpenRouter, then Opus on OpenRouter
cfg["fallback_providers"] = [
    {
        "provider": "openrouter",
        "model": "google/gemini-3-flash-preview",
    },
    {
        "provider": "openrouter",
        "model": "anthropic/claude-opus-4-6",
    },
]

# Delegation/subagents also use MiniMax
cfg.setdefault("delegation", {})
cfg["delegation"]["model"] = "MiniMax-M2.7-highspeed"
cfg["delegation"]["provider"] = "minimax"
cfg["delegation"]["base_url"] = "https://api.minimax.io/anthropic"

# Auxiliary tasks (memory, compression, vision, etc.) also use MiniMax
_aux = {
    "provider": "minimax",
    "model": "MiniMax-M2.7-highspeed",
    "base_url": "https://api.minimax.io/anthropic",
}
cfg["auxiliary"] = {
    "vision": dict(_aux),
    "web_extract": dict(_aux),
    "compression": dict(_aux),
    "approval": dict(_aux),
}

# Yolo mode — skip all dangerous command approval prompts
cfg["approvals"] = {"mode": "off"}

# Clean up stale keys from previous config
for stale_key in ("fallback_model", "fallback_provider", "smart_model_routing"):
    cfg.pop(stale_key, None)

c.write_text(yaml.dump(cfg, default_flow_style=False))
print(f"config.yaml written — primary: MiniMax-M2.7, fallback: gemini-flash -> opus", flush=True)

# --- auth.json: minimax as active provider ---
a = h / "auth.json"
or_key = os.environ.get("OPENROUTER_API_KEY", "")

auth_data = {
    "version": 1,
    "providers": {
        "openrouter": {
            "tokens": {
                "api_key": or_key,
            },
        },
    },
    "active_provider": "minimax",
}
a.write_text(json.dumps(auth_data, indent=2))
print(f"auth.json written — active: minimax, openrouter fallback: {len(or_key)} chars", flush=True)

from gateway.run import main
main()
