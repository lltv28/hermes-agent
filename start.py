import json, os
from pathlib import Path

h = Path(os.environ.get("HERMES_HOME", "/app/.hermes"))
h.mkdir(parents=True, exist_ok=True)

# --- config.yaml: Gemini Flash 3 primary on OpenRouter ---
c = h / "config.yaml"
import yaml

cfg = {}
if c.exists():
    try:
        cfg = yaml.safe_load(c.read_text()) or {}
    except Exception:
        cfg = {}

# Primary: Gemini Flash 3 via OpenRouter
cfg["model"] = "google/gemini-3-flash-preview"
cfg["provider"] = "openrouter"

# Fallback chain: Opus on OpenRouter
cfg["fallback_providers"] = [
    {
        "provider": "openrouter",
        "model": "anthropic/claude-opus-4-6",
    },
]

# Delegation/subagents also use Gemini Flash 3
cfg.setdefault("delegation", {})
cfg["delegation"]["model"] = "google/gemini-3-flash-preview"
cfg["delegation"]["provider"] = "openrouter"

# Auxiliary tasks (memory, compression, vision, etc.) also use Gemini Flash 3
_aux = {
    "provider": "openrouter",
    "model": "google/gemini-3-flash-preview",
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
print("config.yaml written -- primary: gemini-3-flash, fallback: opus", flush=True)

# --- auth.json: openrouter as active provider ---
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
    "active_provider": "openrouter",
}
a.write_text(json.dumps(auth_data, indent=2))
print("auth.json written -- active: openrouter, key: " + str(len(or_key)) + " chars", flush=True)

from gateway.run import main
main()
