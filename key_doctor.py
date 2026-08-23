"""P3.3a — the key doctor. Probes one ring slot against the live wire and prints
the server's own verdict: HTTP code + error body snippet. Key material is never
printed; remote error bodies never echo the key back. Courier the whole output.

Branches:
  bare urllib 200            -> key loved as-is (adapters need nothing).
  nametag 200                -> edge gate bounced the bare signature only (error
                                1010); the nametag header already rides the adapters.
  nametag 404 model_not_found -> KEY VALID, MODEL RETIRED — auth passed, the model
                                slug is dead. Read the roster probe below and the
                                Architect re-pins LANE_MODELS from truth.
  anything else              -> courier the whole card; the Architect rules it.

Exit 0 = the key is loved. Exit 1 = the server spoke / the wire failed — the
printed verdict is the diagnosis.
"""
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

from tars.core.keys import load_ring, parse_env_file
from tars.core.router import LANE_MODELS

URL = "https://api.groq.com/openai/v1/chat/completions"
MODELS_URL = "https://api.groq.com/openai/v1/models"
NAMETAG = "tars-core/1.0 (resident, Cooper's machine)"  # the adapters' exact header


def _probe(key, model: str, user_agent: str | None, label: str) -> tuple:
    """Returns (ok, http_code, body_snippet) — ok only on a real spoken reply."""
    body = json.dumps({"model": model,
                       "messages": [{"role": "user", "content": "ping"}]}).encode("utf-8")
    headers = {"Authorization": f"Bearer {key.key}", "Content-Type": "application/json"}
    if user_agent is not None:
        headers["User-Agent"] = user_agent
    request = urllib.request.Request(URL, data=body, method="POST", headers=headers)
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


def _roster(key) -> None:
    """GET /models under the nametag: this key's own eyeball of what is alive.
    Model ids are public catalog data, courier-safe — no key material."""
    request = urllib.request.Request(MODELS_URL, method="GET", headers={
        "Authorization": f"Bearer {key.key}", "User-Agent": NAMETAG})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            ids = sorted(m.get("id", "") for m in json.loads(response.read().decode("utf-8")).get("data", []))
    except Exception as exc:  # noqa: BLE001 — a roster failure never masks the main verdict
        print(f"[roster] unavailable — {type(exc).__name__}: {exc}")
        return
    print(f"[roster] this key sees {len(ids)} live models:")
    for model_id in ids:
        print(f"  - {model_id}")


def main() -> int:
    default = Path(r"C:\TARS\data") if os.name == "nt" else Path.home() / ".tars"
    data_dir = Path(os.environ.get("TARS_DATA", str(default)))
    secrets = data_dir.parent / "secrets.env"
    source = parse_env_file(secrets) if secrets.is_file() else {}
    ring = load_ring(source)
    if not ring.keys():
        print("keys refused — secrets.env absent, empty, or unreadable")
        return 1
    key = ring.keys()[0]  # slot #1 speaks for the batch
    model = LANE_MODELS[("groq", "fast")]
    print(f"probing slot #{key.index} ({key.visible_name}) — groq fast lane, {model}")
    bare, _code, _snip = _probe(key, model, None, "bare urllib hello")
    if bare:
        print("VERDICT: the key is loved as-is. Re-run first_call.py for the full ceremony card.")
        return 0
    greeted, code, snippet = _probe(key, model, NAMETAG, "honest nametag")
    if greeted:
        print("VERDICT: the nametag opens the door — Cloudflare was bouncing the bare urllib "
              "signature (error 1010), NOT the key. The adapters already wear this nametag. "
              "Re-run first_call.py.")
        return 0
    _roster(key)
    if code == 404 and "model_not_found" in snippet:
        print("VERDICT: KEY VALID, MODEL RETIRED — the door opened, auth passed, and Groq's "
              "own API answered: the slug is dead, the key is not. The roster above is ground "
              "truth; the Architect pins LANE_MODELS from it.")
        return 1
    if code in (401, 403) and "1010" not in snippet:
        print("VERDICT: the key itself is refused (401/403 without the edge ban) — revoke and "
              "mint a fresh one at console.groq.com for that slot.")
        return 1
    print("VERDICT: still refused under the nametag — courier this whole card (roster included); "
          "the Architect rules it from here.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
