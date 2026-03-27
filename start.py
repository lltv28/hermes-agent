import json, os
  from pathlib import Path

  h = Path(os.environ.get("HERMES_HOME", "/app/.hermes"))
  h.mkdir(parents=True, exist_ok=True)

  # Write config.yaml
  c = h / "config.yaml"
  c.write_text(
      "model:\n"
      "  provider: openai-codex\n"
      "  default: gpt-5.4\n"
      "  base_url: https://chatgpt.com/backend-api/codex\n"
  )
  print(f"config.yaml written: {c.read_text()}", flush=True)

  # Write auth.json
  a = h / "auth.json"
  d = json.loads(a.read_text()) if a.exists() else {}
  rt = os.environ.get("CODEX_REFRESH_TOKEN", "")
  d["openai-codex"] = {
      "tokens": {"access_token": "", "refresh_token": rt},
      "auth_mode": "chatgpt",
  }
  d["active_provider"] = "openai-codex"
  a.write_text(json.dumps(d, indent=2))
  print(f"auth.json written, refresh_token length: {len(rt)}", flush=True)       

  # Start gateway
  from gateway.run import main
  main()
