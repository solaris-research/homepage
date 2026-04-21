#!/usr/bin/env python3
"""
build.py — render content/*.md into index.html

For collaborators:
  Just edit the .md files in content/. Then either:
    - push to main (a GitHub Action runs this script automatically), OR
    - run `python3 build.py` locally to regenerate index.html yourself.

The script finds <!-- BEGIN:name --> ... <!-- END:name --> markers inside
index.html and replaces what's between them with HTML rendered from
content/name.md. Do NOT hand-edit code between those markers — it'll be
overwritten on the next build.

No external dependencies: the Markdown used here is deliberately tiny
(paragraphs, *em*, **strong**, [link](url), - bullets, ## headings).
"""
from __future__ import annotations

import html
import pathlib
import re
import sys
from dataclasses import dataclass

ROOT = pathlib.Path(__file__).resolve().parent
CONTENT = ROOT / "content"
INDEX = ROOT / "index.html"


# ---------------------------------------------------------------------------
# Tiny Markdown renderer (intentionally minimal — only what this site uses)
# ---------------------------------------------------------------------------

_MD_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_MD_STRONG = re.compile(r"\*\*([^*]+)\*\*")
_MD_EM = re.compile(r"(?<!\*)\*([^*]+)\*(?!\*)")


def strip_html_comments(text: str) -> str:
    """Drop <!-- ... --> blocks from Markdown (used for author notes)."""
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)


def render_inline(text: str) -> str:
    """Inline Markdown: links, bold, italic. Everything else passes through."""
    text = _MD_LINK.sub(r'<a href="\2">\1</a>', text)
    text = _MD_STRONG.sub(r"<strong>\1</strong>", text)
    text = _MD_EM.sub(r"<em>\1</em>", text)
    return text


def _stagger(base: int, step: int, count: int) -> list[int]:
    return [base + step * i for i in range(count)]


def render_paragraphs(md: str, base: int = 80, step: int = 80) -> str:
    """Render plain prose: blank-line-separated paragraphs, with stagger."""
    md = strip_html_comments(md).strip()
    if not md:
        return ""
    paras = [p.strip() for p in re.split(r"\n\s*\n", md) if p.strip()]
    delays = _stagger(base, step, len(paras))
    out = []
    for p, d in zip(paras, delays):
        out.append(
            f'<p class="reveal" style="--d:{d}ms">\n  {render_inline(p)}\n</p>'
        )
    return "\n".join(out)


def render_topic_list(md: str) -> str:
    """Markdown bullet list -> <ul class="topic-list"> with staggered reveals."""
    md = strip_html_comments(md).strip()
    items = [
        line[2:].strip()
        for line in md.splitlines()
        if line.strip().startswith("- ")
    ]
    if not items:
        return ""
    delays = _stagger(80, 50, len(items))
    lis = "\n".join(
        f'    <li class="reveal" style="--d:{d}ms">\n      {render_inline(item)}\n    </li>'
        for item, d in zip(items, delays)
    )
    return f'<ul class="topic-list">\n{lis}\n  </ul>'


# ---------------------------------------------------------------------------
# Structured sections: parse "## Heading" + "- Key: Value" blocks
# ---------------------------------------------------------------------------


@dataclass
class Entry:
    heading: str
    body: str  # free-text body between this heading and the next one
    fields: dict[str, str]  # "Key: Value" bullets parsed out of body


def parse_entries(md: str) -> list[Entry]:
    md = strip_html_comments(md)
    # Split on "## " at start of line
    chunks = re.split(r"(?m)^##\s+", md)
    entries: list[Entry] = []
    for chunk in chunks[1:]:  # first chunk is pre-heading preamble
        lines = chunk.splitlines()
        heading = lines[0].strip()
        rest = "\n".join(lines[1:]).strip()
        fields: dict[str, str] = {}
        body_lines: list[str] = []
        for raw in rest.splitlines():
            line = raw.strip()
            m = re.match(r"- +([A-Za-z][A-Za-z0-9 _-]*):\s+(.+)", line)
            if m:
                fields[m.group(1).strip().lower()] = m.group(2).strip()
            else:
                body_lines.append(raw)
        body = "\n".join(body_lines).strip()
        entries.append(Entry(heading=heading, body=body, fields=fields))
    return entries


def preamble(md: str) -> str:
    """Text above the first '## ' heading."""
    md = strip_html_comments(md)
    parts = re.split(r"(?m)^##\s+", md, maxsplit=1)
    return parts[0].strip()


def render_team(md: str) -> str:
    entries = parse_entries(md)
    if not entries:
        return ""
    delays = _stagger(80, 50, len(entries))
    figures = []
    for e, d in zip(entries, delays):
        name = html.escape(e.heading)
        link = e.fields.get("link", "#")
        photo = e.fields.get("photo", "")
        role = html.escape(e.fields.get("role", ""))
        img = (
            f'<img src="{html.escape(photo)}" alt="{name}" loading="lazy" '
            f'onerror="this.style.display=\'none\'" />'
            if photo
            else ""
        )
        figures.append(
            f'    <figure class="team-photo reveal" style="--d:{d}ms">\n'
            f'      <a href="{html.escape(link)}" rel="noopener noreferrer" target="_blank">\n'
            f"        {img}\n"
            f"        <figcaption>{name}</figcaption>\n"
            f"      </a>\n"
            f'      <p class="team-photo__role">{role}</p>\n'
            f"    </figure>"
        )
    return '<div class="team-photos">\n' + "\n".join(figures) + "\n  </div>"


def render_collaborators(md: str) -> str:
    entries = parse_entries(md)
    if not entries:
        return ""
    delays = _stagger(80, 50, len(entries))
    links = []
    for e, d in zip(entries, delays):
        name = html.escape(e.heading)
        url = html.escape(e.fields.get("url", "#"))
        logo = e.fields.get("logo", "")
        if logo:
            inner = (
                f'<img src="{html.escape(logo)}" alt="{name}" loading="lazy" '
                f'onerror="this.style.display=\'none\';this.nextElementSibling.style.display=\'inline\'" />\n'
                f'        <span class="partner-logo__wordmark" style="display:none">{name}</span>'
            )
        else:
            inner = f'<span class="partner-logo__wordmark">{name}</span>'
        links.append(
            f'    <a class="partner-logo reveal" style="--d:{d}ms" href="{url}" rel="noopener noreferrer" title="{name}">\n'
            f"        {inner}\n"
            f"    </a>"
        )
    return '<div class="partners-grid">\n' + "\n".join(links) + "\n  </div>"


def render_news(md: str) -> str:
    entries = parse_entries(md)
    if not entries:
        return ""
    delays = _stagger(80, 80, len(entries))
    lis = []
    for e, d in zip(entries, delays):
        date = html.escape(e.heading)
        text = render_inline(e.body or "")
        lis.append(
            f'    <li class="updates-list__item reveal" style="--d:{d}ms">\n'
            f'      <span class="updates-list__date">{date}</span>\n'
            f'      <span class="updates-list__text">{text}</span>\n'
            f"    </li>"
        )
    return '<ul class="updates-list">\n' + "\n".join(lis) + "\n  </ul>"


def render_opportunities(md: str) -> str:
    intro = preamble(md)
    entries = parse_entries(md)
    parts = []
    if intro:
        parts.append(
            f'<p class="opps-band__intro reveal" style="--d:80ms">\n'
            f"  {render_inline(intro)}\n"
            f"</p>"
        )
    if entries:
        delays = _stagger(140, 50, len(entries))
        lis = "\n".join(
            f'    <li class="reveal" style="--d:{d}ms">\n'
            f"      <strong>{html.escape(e.heading)}.</strong> {render_inline(e.body)}\n"
            f"    </li>"
            for e, d in zip(entries, delays)
        )
        parts.append(f'<ul class="opps-list">\n{lis}\n  </ul>')
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Injection: replace content between <!-- BEGIN:name --> and <!-- END:name -->
# ---------------------------------------------------------------------------

RENDERERS = {
    "mission": render_paragraphs,
    "thesis": render_paragraphs,
    "topics": render_topic_list,
    "team": render_team,
    "collaborators": render_collaborators,
    "news": render_news,
    "opportunities": render_opportunities,
}


def inject(html_text: str, name: str, rendered: str) -> str:
    pattern = re.compile(
        rf"(<!--\s*BEGIN:{re.escape(name)}\s*-->)(.*?)(<!--\s*END:{re.escape(name)}\s*-->)",
        re.DOTALL,
    )
    if not pattern.search(html_text):
        print(f"  warning: no <!-- BEGIN:{name} --> / <!-- END:{name} --> markers in index.html; skipping", file=sys.stderr)
        return html_text
    return pattern.sub(lambda m: f"{m.group(1)}\n  {rendered}\n  {m.group(3)}", html_text)


def main() -> int:
    if not INDEX.exists():
        print(f"error: {INDEX} not found", file=sys.stderr)
        return 1
    html_text = INDEX.read_text(encoding="utf-8")
    updated = html_text

    for name, render in RENDERERS.items():
        src = CONTENT / f"{name}.md"
        if not src.exists():
            print(f"  skipping {name}: {src} not found")
            continue
        md = src.read_text(encoding="utf-8")
        rendered = render(md)
        updated = inject(updated, name, rendered)
        print(f"  rendered {name} ({len(rendered)} chars)")

    if updated != html_text:
        INDEX.write_text(updated, encoding="utf-8")
        print(f"wrote {INDEX}")
    else:
        print("no changes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
