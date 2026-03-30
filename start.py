import json, os
from pathlib import Path

h = Path(os.environ.get("HERMES_HOME", "/app/.hermes"))
h.mkdir(parents=True, exist_ok=True)

# --- config.yaml: Gemini 3 Flash default, smart routing to Codex for complex tasks ---
c = h / "config.yaml"
import yaml

cfg = {}
if c.exists():
    try:
        cfg = yaml.safe_load(c.read_text()) or {}
    except Exception:
        cfg = {}

# Default: cheap model for most chats
cfg["model"] = "google/gemini-3-flash-preview"
cfg["provider"] = "openrouter"

# Fallback chain: Codex OAuth first, then Opus on OpenRouter
cfg["fallback_providers"] = [
    {
        "provider": "openai-codex",
        "model": "gpt-5.4",
        "base_url": "https://chatgpt.com/backend-api/codex",
    },
    {
        "provider": "openrouter",
        "model": "anthropic/claude-opus-4-6",
    },
]

# Remove smart_model_routing if it was set as a bool (hermes expects a dict)
cfg.pop("smart_model_routing", None)

# Delegation/subagents use the strong model
cfg.setdefault("delegation", {})
cfg["delegation"]["model"] = "gpt-5.4"
cfg["delegation"]["provider"] = "openai-codex"

# Remove any stale codex-only or gpt-5 references from top-level keys
for key in list(cfg.keys()):
    if key in ("model", "provider", "fallback_providers", "smart_model_routing", "delegation"):
        continue
    val = str(cfg[key]).lower()
    if "codex" in val and "openai-codex" not in val:
        del cfg[key]

c.write_text(yaml.dump(cfg, default_flow_style=False))
print(f"config.yaml written — default: gemini-3-flash, fallback: codex -> opus", flush=True)

# --- auth.json: openrouter as primary, codex as secondary ---
a = h / "auth.json"
api_key = os.environ.get("OPENROUTER_API_KEY", "")
rt = os.environ.get("CODEX_REFRESH_TOKEN", "")

auth_data = {
    "version": 1,
    "providers": {
        "openrouter": {
            "tokens": {
                "api_key": api_key,
            },
        },
        "openai-codex": {
            "tokens": {
                "access_token": "placeholder",
                "refresh_token": rt,
            },
            "auth_mode": "chatgpt",
        },
    },
    "active_provider": "openrouter",
}
a.write_text(json.dumps(auth_data, indent=2))
print(f"auth.json written — active: openrouter, codex rt: {len(rt)} chars", flush=True)

from gateway.run import main
main()
