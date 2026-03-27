import json, os                                                                
from pathlib import Path
h = Path(os.environ.get("HERMES_HOME", "/app/.hermes"))
h.mkdir(parents=True, exist_ok=True)                                           
                                                                                 
c = h / "config.yaml"                                                          
c.write_text("model:\n  provider: openai-codex\n  default: gpt-5.4\n  base_url:
 https://chatgpt.com/backend-api/codex\n")
print("config.yaml written", flush=True)

a = h / "auth.json"
rt = os.environ.get("CODEX_REFRESH_TOKEN", "")
auth_data = {
    "version": 1,
    "providers": {
        "openai-codex": {
            "tokens": {
                "access_token": "placeholder",
                "refresh_token": rt
            },
            "auth_mode": "chatgpt"
        }
    },
    "active_provider": "openai-codex"
}
a.write_text(json.dumps(auth_data, indent=2))
print("auth.json written, refresh_token length: " + str(len(rt)), flush=True)  

from gateway.run import main
main()
