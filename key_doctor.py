"""P3.3a — the key doctor. The ceremony said: six keys, six fast refusals. This
probe asks the wire WHY (once, one key, the declared fast-lane model) and prints
the server's own verdict: HTTP code + error body snippet. Key material is never
printed; remote error bodies never echo the key back. Courier the whole output.

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


def _probe(key, model: str, user_agent: str | None, label: str) -> bool:
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
            return True
    except urllib.error.HTTPError as exc:
        snippet = exc.read().decode("utf-8", errors="replace")[:160]
        print(f"[{label}] HTTP {exc.code} — server says: {snippet}")
        return False
    except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as exc:
        print(f"[{label}] WIRE FAILURE — {type(exc).__name__}: {exc}")
        return False


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
    bare = _probe(key, model, None, "bare urllib hello")
    if bare:
        print("VERDICT: the key is loved as-is. Re-run first_call.py for the full ceremony card.")
        return 0
    greeted = _probe(key, model, "tars-core/1.0 (resident, Cooper's machine)", "honest nametag")
    if greeted:
        print("VERDICT: the nametag opens the door — Cloudflare was bouncing the bare urllib "
              "signature (error 1010), NOT the key. One header line joins both adapters.")
        return 0
    print("VERDICT: still refused under the nametag — the door wants the OFFICIAL client "
          "(staged SDK step comes next) OR the key bytes themselves are retired/wrong. "
          "Courier this whole card; the Architect rules it from here.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
