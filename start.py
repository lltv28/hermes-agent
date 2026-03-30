import json, os
from pathlib import Path

h = Path(os.environ.get("HERMES_HOME", "/app/.hermes"))
h.mkdir(parents=True, exist_ok=True)

# Only write config.yaml if it doesn't exist (preserve Sage's runtime config)
c = h / "config.yaml"
if not c.exists():
    cfg = "model: google/gemini-3-flash-preview\n"
    cfg += "provider: openrouter\n"
    c.write_text(cfg)
    print("config.yaml written (fresh)", flush=True)
else:
    print("config.yaml exists, preserving", flush=True)

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
