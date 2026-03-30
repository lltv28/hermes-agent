import json, os
from pathlib import Path

h = Path(os.environ.get("HERMES_HOME", "/app/.hermes"))
h.mkdir(parents=True, exist_ok=True)

# Ensure config.yaml has no codex references — purge and rewrite provider settings
c = h / "config.yaml"
if c.exists():
    existing = c.read_text()
    # Strip any codex provider lines, preserve everything else
    lines = [l for l in existing.splitlines() if "codex" not in l.lower()]
    c.write_text("\n".join(lines) + "\n")
    print("config.yaml cleaned (removed codex)", flush=True)
else:
    c.write_text("model: google/gemini-3-flash-preview\nprovider: openrouter\n")
    print("config.yaml written (fresh)", flush=True)

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
