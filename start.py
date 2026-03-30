import json, os
from pathlib import Path

h = Path(os.environ.get("HERMES_HOME", "/app/.hermes"))
h.mkdir(parents=True, exist_ok=True)

# Write clean config.yaml with correct model/provider
c = h / "config.yaml"
import yaml
cfg = {}
if c.exists():
    try:
        cfg = yaml.safe_load(c.read_text()) or {}
    except Exception:
        cfg = {}
# Force correct model and provider
cfg["model"] = "google/gemini-3-flash-preview"
cfg["provider"] = "openrouter"
# Remove any stale codex/gpt-5 references
for key in list(cfg.keys()):
    val = str(cfg[key]).lower()
    if "codex" in val or "gpt-5" in val:
        del cfg[key]
c.write_text(yaml.dump(cfg, default_flow_style=False))
print("config.yaml written, model: google/gemini-3-flash-preview", flush=True)

# Write auth.json with openrouter as active provider
a = h / "auth.json"
api_key = os.environ.get("OPENROUTER_API_KEY", "")
auth_data = {
    "version": 1,
    "providers": {
        "openrouter": {
            "tokens": {
                "api_key": api_key
            }
        }
    },
    "active_provider": "openrouter"
}
a.write_text(json.dumps(auth_data, indent=2))
print("auth.json written, provider: openrouter", flush=True)

from gateway.run import main
main()
