"""The two keyless search lanes (command-grammar §5): YouTube ytsearch-styled
structured fetch and the DuckDuckGo html lane.

Both lanes are keyless but NETWORKED — the builders and parsers below are the
real, reviewable codepaths; the sandbox never lifts them (fixtures replay
recorded payloads pinned in-code). Contract honesty: results carry
{rank, title, source, url} triples for the APP's result cards; an utterance
that asks for results never claims rows it didn't pull (§16).
"""
import json
import re
import urllib.parse
import urllib.request

RESULTS_MAX = 3


def youtube_url(query: str) -> str:
    """The keyless ytsearch endpoint shape."""
    return "https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(query)


def ddg_url(query: str) -> str:
    """The DuckDuckGo html endpoint shape."""
    return "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote_plus(query)


def parse_youtube(html: str) -> list:
    """videoRenderer chunks -> [{rank, title, source, url}] in page order."""
    rows = []
    chunks = re.findall(r'\{"videoRenderer":\{.*?\}\}\}', html)
    for chunk in chunks:
        vid = re.search(r'"videoId":"([^"]+)"', chunk)
        title = re.search(r'"title":\{"runs":\[\{"text":"((?:[^"\\]|\\.)*)"', chunk)
        owner = re.search(r'"ownerText":\{"runs":\[\{"text":"((?:[^"\\]|\\.)*)"', chunk)
        if not (vid and title and owner):
            continue  # a renderer missing its fields is skipped honestly, never half-credited
        rows.append({"rank": len(rows) + 1,
                     "title": json.loads(f'"{title.group(1)}"'),
                     "source": json.loads(f'"{owner.group(1)}"'),
                     "url": f"https://www.youtube.com/watch?v={vid.group(1)}"})
    return rows


def parse_ddg(html: str) -> list:
    """result__a / result__url pairs -> [{rank, title, source, url}] in page order."""
    links = re.findall(r'class="result__a"[^>]*href="([^"]*uddg=([^"&]+)[^"]*)"[^>]*>(.*?)</a>', html)
    domains = re.findall(r'class="result__url"[^>]*>\s*(?:https?://)?([^<\s&]+)', html)
    rows = []
    for index, (_href, uddg, title_html) in enumerate(links):
        url = urllib.parse.unquote(uddg)
        title = re.sub(r"<[^>]+>", "", title_html).strip()
        source = domains[index].strip() if index < len(domains) else urllib.parse.urlparse(url).netloc
        rows.append({"rank": len(rows) + 1, "title": title, "source": source, "url": url})
    return rows


def _http_get(url: str) -> str:
    """The real transport — keyless but networked; first live pull awaits the AiO (never sandbox-fired)."""
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 TARS/1.0"})
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.read().decode("utf-8", "replace")


class SearchLanes:
    """One facade, two lanes; transport is an injected seam so fixtures own the sandbox."""

    def __init__(self, fetch=None):
        self._fetch = fetch or _http_get

    def youtube(self, query: str) -> list:
        return parse_youtube(self._fetch(youtube_url(query)))[:RESULTS_MAX]

    def web(self, query: str) -> list:
        return parse_ddg(self._fetch(ddg_url(query)))[:RESULTS_MAX]


class FixtureSearch:
    """Replayed payloads keyed by the exact URL the lane would build — deterministic to the byte."""

    def __init__(self, payloads: dict):
        self._payloads = dict(payloads)
        self.calls = []

    def __call__(self, url: str) -> str:
        self.calls.append(url)
        return self._payloads[url]  # KeyError = the test wired a wrong URL — loud, not silent
