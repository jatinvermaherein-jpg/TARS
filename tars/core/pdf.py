"""The PDF seam (bible §24, P-CORE-12) — a pure-stdlib, MINIMAL text-layer extractor.

HONEST ENVELOPE (declared, battery-pinned at the edges — never a guess):
StdPdfReader reads garden-variety text-layer PDFs whose spine matches:
    %PDF header -> a /Pages root carrying /Kids [N 0 R ...] (the Kids array IS
    the page order, so page numbering is truthful) -> each kid a /Page object
    with /Contents <refs> -> content streams FlateDecode'd -> text shown with
    the Tj / TJ operators. Literal-string escapes honored: \\n \\r \\t \\( \\) \\\\;
    a backslash before anything else yields that char, per the PDF literal law.
Anything outside the envelope — no header, encrypted (/Encrypt), nested Pages
subtrees, missing Kids, uncompressed streams, zero Tj/TJ text anywhere — raises
PdfOpaque and the row answers LINE_PDF_OPAQUE. Scanned pages have no text
layer, so they land there honestly. M-era may import-guard pypdf by decree;
that is NOT this phase.
"""
import re
import zlib
from pathlib import Path

_PAGE_KIDS = re.compile(rb"/Type\s*/Pages\b.*?/Kids\s*\[(.*?)\]", re.S)
_PAGE_OBJ = re.compile(rb"/Type\s*/Page\b")
_CONTENTS_LIST = re.compile(rb"/Contents\s*\[(.*?)\]", re.S)
_CONTENTS_ONE = re.compile(rb"/Contents\s+(\d+)\s+0\s+R")
_REF = re.compile(rb"(\d+)\s+0\s+R")
_HEADER = b"%PDF"


class PdfOpaque(Exception):
    """The honest refusal signal: this file is outside the text-layer envelope."""


class PdfBook:
    """An opened PDF: the page count + page-pinned text (1-indexed pages)."""

    def __init__(self, pages: list):
        self._pages = list(pages)

    @property
    def pages(self) -> int:
        return len(self._pages)

    def page_text(self, n: int) -> str:
        if not 1 <= n <= len(self._pages):
            raise IndexError(f"page {n} outside 1..{len(self._pages)}")
        return self._pages[n - 1]


def _object_body(raw: bytes, number: int):
    """The body of indirect object `number 0 obj` ... `endobj`; None when absent."""
    marker = re.compile(rb"(?<!\d)" + str(number).encode() + rb"\s+0\s+obj\b")
    hit = marker.search(raw)
    if not hit:
        return None
    end = raw.find(b"endobj", hit.end())
    if end < 0:
        return None
    return raw[hit.end():end]


def _literal_strings(data: bytes):
    """(text) literals in order, escapes resolved. Yields (text, end_index) pairs."""
    pos = 0
    while pos < len(data):
        if data[pos:pos + 1] != b"(":
            pos += 1
            continue
        depth = 1
        out = []
        i = pos + 1
        while i < len(data) and depth:
            ch = data[i:i + 1]
            if ch == b"\\" and i + 1 < len(data):
                nxt = data[i + 1:i + 2]
                out.append({b"n": "\n", b"r": "\r", b"t": "\t", b"(": "(", b")": ")",
                            b"\\": "\\"}.get(nxt, nxt.decode("latin-1")))
                i += 2
                continue
            if ch == b"(":
                depth += 1
            elif ch == b")":
                depth -= 1
                if depth == 0:
                    break
            out.append(ch.decode("latin-1"))
            i += 1
        yield "".join(out), i + 1
        pos = i + 1


def _stream_text(stream: bytes) -> str:
    """Text from one decompressed content stream: Tj shows its literal, TJ joins its
    array's literals (the kerning numbers are spacing, not words). One op = one line."""
    lines = []
    for match in re.finditer(rb"\[(.*?)\]\s*TJ|\(", stream, re.S):
        if match.group(1) is not None:  # a [ ... ] TJ array
            joined = "".join(text for text, _end in _literal_strings(match.group(1)))
            lines.append(joined)
            continue
        # a bare literal — consult what follows: only the Tj operator shows it
        text, end = next(_literal_strings(stream[match.end() - 1:]))
        if stream[end + match.end() - 1:end + match.end() + 2].lstrip().startswith(b"Tj"):
            lines.append(text)
    return "\n".join(line for line in lines if line)


class StdPdfReader:
    """The standing extractor: pure stdlib, the envelope above, honest refusals only."""

    def open(self, path) -> PdfBook:
        raw = Path(path).read_bytes()
        if not raw.startswith(_HEADER) or b"/Encrypt" in raw:
            raise PdfOpaque("no %PDF header, or the file is encrypted")
        kids_match = _PAGE_KIDS.search(raw)
        if kids_match is None:
            raise PdfOpaque("no /Pages /Kids spine (nested subtrees are outside the envelope)")
        pages = []
        any_text = False
        for kid in _REF.findall(kids_match.group(1)):
            page_obj = _object_body(raw, int(kid))
            if page_obj is None or _PAGE_OBJ.search(page_obj) is None:
                raise PdfOpaque(f"/Kids entry {kid.decode()} is not a readable /Page object")
            contents_match = _CONTENTS_LIST.search(page_obj) or _CONTENTS_ONE.search(page_obj)
            if contents_match is None:
                raise PdfOpaque("a /Page object carries no readable /Contents reference")
            refs = (_REF.findall(contents_match.group(1))
                    if contents_match.re is _CONTENTS_LIST else [contents_match.group(1)])
            text_parts = []
            for ref in refs:
                body = _object_body(raw, int(ref))
                if body is None or b"stream" not in body or b"/FlateDecode" not in body:
                    raise PdfOpaque("a /Contents stream is missing or not FlateDecode'd")
                start = body.find(b"stream") + len(b"stream")
                if body[start:start + 2] == b"\r\n":
                    start += 2
                elif body[start:start + 1] in (b"\n", b"\r"):
                    start += 1
                end = body.find(b"endstream", start)
                try:
                    text_parts.append(_stream_text(zlib.decompress(body[start:end].rstrip(b"\r\n"))))
                except zlib.error as exc:
                    raise PdfOpaque("a FlateDecode stream refused to decompress") from exc
            page_text = "\n".join(part for part in text_parts if part).strip("\n")
            any_text = any_text or bool(page_text.strip())
            pages.append(page_text)
        if not pages or not any_text:
            raise PdfOpaque("no Tj/TJ text anywhere — a scanned page layer, most likely")
        return PdfBook(pages)


class FixturePdf:
    """The suite's library: scripted pages per path; an unknown path is KeyError-loud
    (the fixture never invents a book)."""

    def __init__(self, books: dict):
        self._books = {str(k): list(v) for k, v in books.items()}

    def open(self, path) -> PdfBook:
        return PdfBook(self._books[str(path)])
