"""Office Studio — pure-stdlib OOXML (P-CORE-6).

LAW (phase decree): python-docx / python-pptx / lxml are FORBIDDEN. A .docx /
.pptx is a zip of XML, so the studio emits the minimal VALID part set by hand
with the standard library alone: docx = [Content_Types].xml + _rels/.rels +
word/document.xml; pptx = [Content_Types].xml + _rels/.rels +
ppt/presentation.xml + ppt/_rels/presentation.xml.rels + ppt/slides/slideN.xml.

Golden-file determinism: every zip entry rides the golden epoch (2026-01-01),
declared part ordering, fixed compression — the same inputs yield the same
container, byte for byte, so the battery pins a container sha256.

Output path per bible §18: finished work lands on the Desktop. nt truth:
%USERPROFILE%\\Desktop. Off-nt (this sandbox): TARS_DATA/desktop — a canon
comment keeps the Windows truth next to the seam. Filename hygiene: readable
title slug, collision -> "Name (2).ext" newest-first, never an overwrite.

Content honesty: packages carry title + body fully but no theme/masters —
mainstream Office opens the content and may offer to normalize on save.
"""
import os
import zipfile
from xml.sax.saxutils import escape

GOLDEN_EPOCH = (2026, 1, 1, 0, 0, 0)  # canon golden zip epoch: determinism, not nostalgia

_XML_DECL = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
_NS_CT = "http://schemas.openxmlformats.org/package/2006/content-types"
_NS_REL = "http://schemas.openxmlformats.org/package/2006/relationships"
_NS_OFFREL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def desktop_dir() -> str:
    """§18 target. Canon: on the AiO this is the user's real Desktop."""
    if os.name == "nt":
        return os.path.join(os.environ.get("USERPROFILE", os.path.expanduser("~")), "Desktop")
    base = os.environ.get("TARS_DATA", os.path.expanduser(os.path.join("~", ".tars")))
    return os.path.join(base, "desktop")  # canon: sandbox fixture dir standing in for the AiO Desktop


def safe_slug(title: str) -> str:
    """Readable filename from a title: keep word chars/spaces/dots/dashes, collapse the rest."""
    kept = "".join(ch for ch in str(title) if ch.isalnum() or ch in " ._-").strip()
    kept = " ".join(kept.split())
    return kept or "Untitled"


def _dedupe(directory: str, name: str) -> str:
    stem, dot, ext = name.rpartition(".")
    candidate = name
    serial = 1
    while os.path.exists(os.path.join(directory, candidate)):
        serial += 1
        candidate = f"{stem} ({serial}).{ext}"
    return candidate


def _write_container(directory: str, name: str, parts: list) -> str:
    os.makedirs(directory, exist_ok=True)
    final = _dedupe(directory, name)
    target = os.path.join(directory, final)
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zf:
        for part_name, payload in parts:
            info = zipfile.ZipInfo(part_name, date_time=GOLDEN_EPOCH)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o600 << 16  # plain file attrs, deterministic across runs
            zf.writestr(info, payload)
    return final


# --- docx ---

_DOCX_TYPES = (_XML_DECL + '<Types xmlns="' + _NS_CT + '">'
               '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
               '<Default Extension="xml" ContentType="application/xml"/>'
               '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument'
               '.wordprocessingml.document.main+xml"/>'
               "</Types>")

_DOCX_RELS = (_XML_DECL + '<Relationships xmlns="' + _NS_REL + '">'
              '<Relationship Id="rId1" Type="' + _NS_OFFREL + '/officeDocument" Target="word/document.xml"/>'
              "</Relationships>")


def _document_xml(title: str, paragraphs: list) -> str:
    lines = [_XML_DECL,
             '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>']
    lines.append(f"<w:p><w:r><w:t>{escape(title)}</w:t></w:r></w:p>")
    for para in paragraphs:
        lines.append(f"<w:p><w:r><w:t>{escape(para)}</w:t></w:r></w:p>")
    lines.append("<w:sectPr/></w:body></w:document>")
    return "".join(lines)


def build_docx(title: str, paragraphs: list, desktop: str = None) -> str:
    """-> the saved filename (Desktop dir created if missing). Pure stdlib, deterministic."""
    directory = desktop or desktop_dir()
    parts = [("[Content_Types].xml", _DOCX_TYPES), ("_rels/.rels", _DOCX_RELS),
             ("word/document.xml", _document_xml(title, paragraphs))]
    return _write_container(directory, f"{safe_slug(title)}.docx", parts)


# --- pptx ---

def _pptx_types(slide_count: int) -> str:
    overrides = "".join(
        f'<Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument'
        f'.presentationml.slide+xml"/>' for i in range(1, slide_count + 1))
    return (_XML_DECL + '<Types xmlns="' + _NS_CT + '">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument'
            '.presentationml.presentation.main+xml"/>'
            + overrides + "</Types>")


_PPTX_ROOT_RELS = (_XML_DECL + '<Relationships xmlns="' + _NS_REL + '">'
                   '<Relationship Id="rId1" Type="' + _NS_OFFREL + '/officeDocument" Target="ppt/presentation.xml"/>'
                   "</Relationships>")


def _presentation_xml(slide_count: int) -> str:
    sld_ids = "".join(f'<p:sldId id="{255 + i}" r:id="rId{i}"/>' for i in range(1, slide_count + 1))
    return (_XML_DECL
            + '<p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
            'xmlns:r="' + _NS_OFFREL + '">'
            f"<p:sldIdLst>{sld_ids}</p:sldIdLst>"
            '<p:sldSz cx="12192000" cy="6858000" type="screen16x9"/><p:notesSz cx="6858000" cy="9144000"/>'
            "</p:presentation>")


def _presentation_rels(slide_count: int) -> str:
    rels = "".join(f'<Relationship Id="rId{i}" Type="{_NS_OFFREL}/slide" Target="slides/slide{i}.xml"/>'
                   for i in range(1, slide_count + 1))
    return _XML_DECL + '<Relationships xmlns="' + _NS_REL + '">' + rels + "</Relationships>"


def _text_shape(shape_id: int, name: str, lines: list) -> str:
    paras = "".join(f"<a:p><a:r><a:t>{escape(line)}</a:t></a:r></a:p>" for line in lines)
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{shape_id}" name="{name}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f"<p:spPr/><p:txBody><a:bodyPr/><a:lstStyle/>{paras}</p:txBody></p:sp>")


def _slide_xml(heading: str, bullets: list) -> str:
    return (_XML_DECL
            + '<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
            'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
            'xmlns:r="' + _NS_OFFREL + '">'
            "<p:cSld><p:spTree>"
            '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/>'
            + _text_shape(2, "Heading", [heading])
            + _text_shape(3, "Bullets", bullets)
            + "</p:spTree></p:cSld></p:sld>")


def build_pptx(title: str, slides: list, desktop: str = None) -> str:
    """slides = [{"heading": str, "bullets": [str]}] — -> the saved filename."""
    directory = desktop or desktop_dir()
    count = len(slides)
    parts = [("[Content_Types].xml", _pptx_types(count)), ("_rels/.rels", _PPTX_ROOT_RELS)]
    parts.append(("ppt/presentation.xml", _presentation_xml(count)))
    parts.append(("ppt/_rels/presentation.xml.rels", _presentation_rels(count)))
    for index, slide in enumerate(slides, 1):
        parts.append((f"ppt/slides/slide{index}.xml", _slide_xml(slide["heading"], slide["bullets"])))
    return _write_container(directory, f"{safe_slug(title)}.pptx", parts)


# --- the ring-drafted outline contract (declared, fixture-stable) ---

def office_prompt(kind: str, topic: str) -> str:
    """The declared drafting ask. Long + keyworded -> routes smart-or-above per the ring gates."""
    if kind == "pptx":
        return ("Draft a slide deck. Topic: " + topic + ". Reply in EXACTLY this plain shape, no commentary: "
                "first line the deck title alone; then per slide one line 'slide: <heading>' followed by up to "
                "four bullet lines starting '- '. Three to five slides. Explain simply, honestly, no invented facts.")
    return ("Draft a short document. Topic: " + topic + ". Reply with the document title alone on the first "
            "line, then three to six short paragraphs, one per line. Plain text only, no commentary, no "
            "markdown; explain simply, honestly, with no invented facts.")


def parse_outline(kind: str, text: str):
    """The ring's plain-text outline -> (title, slides|paragraphs). Malformed rows skip honestly;
    nothing usable -> None (the layer answers the catch-all, never builds a junk file)."""
    lines = [line.strip() for line in str(text).splitlines() if line.strip()]
    if not lines:
        return None
    title, body = lines[0], lines[1:]
    if kind == "pptx":
        slides = []
        for line in body:
            lowered = line.lower()
            if lowered.startswith("slide:"):
                slides.append({"heading": line[len("slide:"):].strip(), "bullets": []})
            elif line.startswith("- ") and slides:
                slides[-1]["bullets"].append(line[2:].strip())
        if not slides and body:
            slides = [{"heading": body[0], "bullets": body[1:]}]
        return (title, slides) if slides else None
    return (title, body) if body else None
