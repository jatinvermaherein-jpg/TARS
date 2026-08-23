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
    body = json.dumps({"model": LANE_MODELS[("groq", "fast")],
                       "messages": [{"role": "user", "content": "ping"}]}).encode("utf-8")
    request = urllib.request.Request("https://api.groq.com/openai/v1/chat/completions",
                                     data=body, method="POST",
                                     headers={"Authorization": f"Bearer {key.key}",
                                              "Content-Type": "application/json"})
    print(f"probing slot #{key.index} ({key.visible_name}) — groq fast lane, one glass of water")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            text = json.loads(response.read().decode("utf-8"))["choices"][0]["message"]["content"]
            print(f"HTTP 200 — REPLY BYTES: {text!r}")
            print("VERDICT: the key is loved. Re-run first_call.py for the full ceremony card.")
            return 0
    except urllib.error.HTTPError as exc:
        snippet = exc.read().decode("utf-8", errors="replace")[:200]
        print(f"HTTP {exc.code} — server says: {snippet}")
        print("VERDICT: 401/403 = the key itself is refused (revoke never happened in transit — "
              "the bytes were born wrong or retired). Fresh keys from console.groq.com next.")
        return 1
    except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as exc:
        print(f"WIRE FAILURE — {type(exc).__name__}: {exc}")
        print("VERDICT: no route to the API (offline / firewall / DNS). The keys never got judged.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
