"""P3.3a — the key doctor. Probes one ring slot against the live wire and prints
the server's own verdict: HTTP code + error body snippet. Key material is never
printed; remote error bodies never echo the key back. Courier the whole output.

Modes:
  python key_doctor.py              -> groq fast lane, slot #1 (bare urllib, then
                                       the honest nametag; roster probe on failure).
  python key_doctor.py openrouter   -> OpenRouter council seat, slot #7 (nametag
                                       from the start — the 1010 lesson is burned
                                       in), then ALWAYS the live :free roster so a
                                       rotated seat can be re-pinned from truth.

Branches:
  200                    -> key loved.
  404 model_not_found    -> KEY VALID, MODEL RETIRED/RENAMED — auth passed; read
                            the roster and the Architect re-pins LANE_MODELS.
  401/403 (no 1010)      -> the key itself is refused — revoke + mint fresh.
  else                   -> courier the whole card; the Architect rules it.

Exit 0 = the key is loved. Exit 2 = keys refused for that provider. Exit 1 =
the server spoke / the wire failed — the printed verdict is the diagnosis.
"""
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

from tars.core.keys import load_ring, parse_env_file
from tars.core.router import LANE_MODELS

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODELS_URL = "https://api.groq.com/openai/v1/models"
OR_URL = "https://openrouter.ai/api/v1/chat/completions"
OR_MODELS_URL = "https://openrouter.ai/api/v1/models"
NAMETAG = "tars-core/1.0 (resident, Cooper's machine)"  # the adapters' exact header


def _probe(url, key, model: str, user_agent: str | None, label: str) -> tuple:
    """Returns (ok, http_code, body_snippet) — ok only on a real spoken reply."""
    body = json.dumps({"model": model,
                       "messages": [{"role": "user", "content": "ping"}]}).encode("utf-8")
    headers = {"Authorization": f"Bearer {key.key}", "Content-Type": "application/json"}
    if user_agent is not None:
        headers["User-Agent"] = user_agent
    request = urllib.request.Request(url, data=body, method="POST", headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            text = json.loads(response.read().decode("utf-8"))["choices"][0]["message"]["content"]
            print(f"[{label}] HTTP 200 — REPLY BYTES: {text!r}")
            return True, 200, ""
    except urllib.error.HTTPError as exc:
        snippet = exc.read().decode("utf-8", errors="replace")[:160]
        print(f"[{label}] HTTP {exc.code} — server says: {snippet}")
        return False, exc.code, snippet
    except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as exc:
        print(f"[{label}] WIRE FAILURE — {type(exc).__name__}: {exc}")
        return False, 0, str(exc)


def _roster(url, key, label: str, free_only: bool) -> list:
    """GET /models under the nametag: this key's own eyeball of what is alive.
    Model ids are public catalog data, courier-safe — no key material."""
    request = urllib.request.Request(url, method="GET", headers={
        "Authorization": f"Bearer {key.key}", "User-Agent": NAMETAG})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            ids = sorted(m.get("id", "") for m in json.loads(response.read().decode("utf-8")).get("data", []))
    except Exception as exc:  # noqa: BLE001 — a roster failure never masks the main verdict
        print(f"[roster] unavailable — {type(exc).__name__}: {exc}")
        return []
    shown = [m for m in ids if m.endswith(":free")] if free_only else ids
    print(f"[roster] {label}: {len(ids)} live models, {len(shown)} shown:")
    for model_id in shown:
        print(f"  - {model_id}")
    return shown


def _load(data_dir: Path):
    secrets = data_dir.parent / "secrets.env"
    source = parse_env_file(secrets) if secrets.is_file() else {}
    return load_ring(source), secrets


def _data_dir() -> Path:
    default = Path(r"C:\TARS\data") if os.name == "nt" else Path.home() / ".tars"
    return Path(os.environ.get("TARS_DATA", str(default)))


def _verdict(code: int, snippet: str, greeted: bool, bare_failed: bool) -> int:
    if greeted:
        if bare_failed:
            print("VERDICT: the nametag opens the door — Cloudflare was bouncing the bare urllib "
                  "signature (error 1010), NOT the key. The adapters already wear this nametag.")
        else:
            print("VERDICT: the key is loved as-is.")
        return 0
    if code == 404 and "model_not_found" in snippet:
        print("VERDICT: KEY VALID, MODEL RETIRED — the door opened, auth passed, and the API's "
              "own answer is: the slug is dead (or rotated off free). The roster above is ground "
              "truth; the Architect re-pins LANE_MODELS from it.")
        return 1
    if code in (401, 403) and "1010" not in snippet:
        print("VERDICT: the key itself is refused (401/403 without the edge ban) — revoke and "
              "mint a fresh one at the provider console for that slot.")
        return 1
    print("VERDICT: still refused under the nametag — courier this whole card (roster included); "
          "the Architect rules it from here.")
    return 1


def main() -> int:
    openrouter_mode = len(sys.argv) > 1 and sys.argv[1].lower() == "openrouter"
    ring, secrets = _load(_data_dir())
    provider = "openrouter" if openrouter_mode else "groq"
    slots = [k for k in ring.keys() if k.provider == provider]
    if not slots:
        print(f"keys refused — no {provider} slots loaded (looked at: {secrets})")
        return 2
    key = slots[0]  # the provider's first slot speaks for its batch

    if openrouter_mode:
        model = LANE_MODELS[("openrouter", "council")]
        print(f"probing slot #{key.index} ({key.visible_name}) — openrouter council seat, {model}")
        ok, code, snippet = _probe(OR_URL, key, model, NAMETAG, "honest nametag")
        _roster(OR_MODELS_URL, key, "openrouter", free_only=True)
        return _verdict(code, snippet, ok, bare_failed=False)

    model = LANE_MODELS[("groq", "fast")]
    print(f"probing slot #{key.index} ({key.visible_name}) — groq fast lane, {model}")
    bare, _code, _snip = _probe(GROQ_URL, key, model, None, "bare urllib hello")
    if bare:
        print("VERDICT: the key is loved as-is. Re-run first_call.py for the full ceremony card.")
        return 0
    greeted, code, snippet = _probe(GROQ_URL, key, model, NAMETAG, "honest nametag")
    if not greeted:
        _roster(GROQ_MODELS_URL, key, "groq", free_only=False)
    return _verdict(code, snippet, greeted, bare_failed=True)


if __name__ == "__main__":
    sys.exit(main())
