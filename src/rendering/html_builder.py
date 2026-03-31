"""Convert TextBlocks into paginated HTML for the Playwright renderer.

Each "slide" is a ``<div class="slide">`` with a fixed width/height.
The Playwright renderer screenshots each slide independently.
"""

import html
import json
import re
from typing import List, Optional

from src.data.text_block import TextBlock
from src.utils.config import Config

# Inline formatting patterns
_BOLD_RE = re.compile(r"\*\*(.+?)\*\*|__(.+?)__")
_ITALIC_RE = re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)|(?<!_)_(?!_)(.+?)(?<!_)_(?!_)")
_INLINE_CODE_RE = re.compile(r"`([^`]+)`")
_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_STRIKETHROUGH_RE = re.compile(r"~~(.+?)~~")


def _apply_inline_formatting(text: str) -> str:
    """Convert markdown inline formatting to HTML spans."""
    escaped = html.escape(text)
    # Order matters: code first (prevent inner parsing), then bold before italic
    escaped = _INLINE_CODE_RE.sub(r'<code class="inline">\1</code>', escaped)
    escaped = _BOLD_RE.sub(r"<strong>\1\2</strong>", escaped)
    escaped = _ITALIC_RE.sub(r"<em>\1\2</em>", escaped)
    escaped = _LINK_RE.sub(r'<a href="\2">\1</a>', escaped)
    escaped = _STRIKETHROUGH_RE.sub(r"<del>\1</del>", escaped)
    return escaped


def _render_paragraph(block: TextBlock) -> str:
    return f"<p>{_apply_inline_formatting(block.data)}</p>"


def _render_title(block: TextBlock) -> str:
    return f'<h1 class="title">{_apply_inline_formatting(block.data)}</h1>'


def _render_header(block: TextBlock) -> str:
    return f"<h2>{_apply_inline_formatting(block.data)}</h2>"


def _render_code(block: TextBlock) -> str:
    lines = block.data.split("\n")
    # First line may contain ```language
    lang = ""
    start = 0
    if lines and lines[0].strip().startswith("```"):
        lang_match = lines[0].strip().lstrip("`").strip()
        if lang_match:
            lang = lang_match
        start = 1
    # Last line may be closing ```
    end = len(lines)
    if end > start and lines[end - 1].strip() == "```":
        end -= 1
    code_text = html.escape("\n".join(lines[start:end]))
    lang_class = f' class="language-{html.escape(lang)}"' if lang else ""
    return f'<div class="code-block"><pre><code{lang_class}>{code_text}</code></pre></div>'


def _render_bullet_list(block: TextBlock) -> str:
    items = block.data.split("\n")
    li_items = "\n".join(
        f"  <li>{_apply_inline_formatting(item)}</li>" for item in items if item.strip()
    )
    return f"<ul>\n{li_items}\n</ul>"


def _render_numbered_list(block: TextBlock) -> str:
    items = block.data.split("\n")
    li_items = "\n".join(
        f"  <li>{_apply_inline_formatting(item)}</li>" for item in items if item.strip()
    )
    return f"<ol>\n{li_items}\n</ol>"


def _render_blockquote(block: TextBlock) -> str:
    lines = block.data.split("\n")
    inner = "<br>\n".join(_apply_inline_formatting(line) for line in lines)
    return f"<blockquote>{inner}</blockquote>"


def _render_horizontal_rule(block: TextBlock) -> str:
    return "<hr>"


def _render_table(block: TextBlock) -> str:
    rows = [r.strip() for r in block.data.strip().split("\n") if r.strip()]
    if not rows:
        return ""

    def parse_row(row: str) -> List[str]:
        cells = row.split("|")
        return [c.strip() for c in cells if c.strip()]

    header_cells = parse_row(rows[0])
    thead = "<tr>" + "".join(f"<th>{_apply_inline_formatting(c)}</th>" for c in header_cells) + "</tr>"

    body_rows = []
    for row in rows[1:]:
        # Skip separator rows (e.g. |---|---|)
        if all(ch in "-| " for ch in row):
            continue
        cells = parse_row(row)
        body_rows.append(
            "<tr>" + "".join(f"<td>{_apply_inline_formatting(c)}</td>" for c in cells) + "</tr>"
        )
    tbody = "\n".join(body_rows)
    return f'<div class="table-wrapper"><table>\n<thead>{thead}</thead>\n<tbody>\n{tbody}\n</tbody>\n</table></div>'


def _render_task_list(block: TextBlock) -> str:
    items = block.data.split("\n")
    li_items = []
    for item in items:
        if not item.strip():
            continue
        if item.startswith("checked:"):
            text = item[len("checked:") :]
            li_items.append(
                f'  <li class="task checked"><span class="checkbox">&#9745;</span> {_apply_inline_formatting(text)}</li>'
            )
        elif item.startswith("unchecked:"):
            text = item[len("unchecked:") :]
            li_items.append(
                f'  <li class="task unchecked"><span class="checkbox">&#9744;</span> {_apply_inline_formatting(text)}</li>'
            )
    return f'<ul class="task-list">\n' + "\n".join(li_items) + "\n</ul>"


def _render_github_code(block: TextBlock) -> str:
    """Render a fetched GitHub code file as a styled file card."""
    payload = json.loads(block.data)
    filename = html.escape(payload["filename"])
    language = html.escape(payload["language"])
    repo = html.escape(f'{payload["owner"]}/{payload["repo"]}')
    path = html.escape(payload["path"])
    code = html.escape(payload["content"].rstrip())
    lang_lower = language.lower()

    return (
        f'<div class="github-file">'
        f'<div class="github-file-header">'
        f'<span class="github-file-icon">📄</span>'
        f'<span class="github-file-name">{filename}</span>'
        f'<span class="github-file-lang">{language}</span>'
        f'</div>'
        f'<div class="github-file-meta">{repo} — {path}</div>'
        f'<div class="code-block"><pre><code class="language-{lang_lower}">{code}</code></pre></div>'
        f'</div>'
    )


def _render_github_notes(block: TextBlock) -> str:
    """Render a fetched GitHub markdown/notes file as a styled card."""
    payload = json.loads(block.data)
    filename = html.escape(payload["filename"])
    repo = html.escape(f'{payload["owner"]}/{payload["repo"]}')
    path = html.escape(payload["path"])
    content = payload["content"].rstrip()

    # Convert the markdown content to simple HTML
    lines_html = []
    for line in content.split("\n"):
        stripped = line.strip()
        if stripped.startswith("## "):
            lines_html.append(f'<h3 class="notes-heading">{_apply_inline_formatting(stripped[3:])}</h3>')
        elif stripped.startswith("# "):
            lines_html.append(f'<h3 class="notes-heading">{_apply_inline_formatting(stripped[2:])}</h3>')
        elif stripped.startswith("- ") or stripped.startswith("* "):
            lines_html.append(f'<li>{_apply_inline_formatting(stripped[2:])}</li>')
        elif stripped:
            lines_html.append(f'<p>{_apply_inline_formatting(stripped)}</p>')
    inner = "\n".join(lines_html)

    return (
        f'<div class="github-file github-notes">'
        f'<div class="github-file-header">'
        f'<span class="github-file-icon">📝</span>'
        f'<span class="github-file-name">{filename}</span>'
        f'<span class="github-file-lang">Notes</span>'
        f'</div>'
        f'<div class="github-file-meta">{repo} — {path}</div>'
        f'<div class="github-notes-content">{inner}</div>'
        f'</div>'
    )


_BLOCK_RENDERERS = {
    "paragraph": _render_paragraph,
    "title": _render_title,
    "header": _render_header,
    "code": _render_code,
    "bullet_list": _render_bullet_list,
    "numbered_list": _render_numbered_list,
    "blockquote": _render_blockquote,
    "horizontal_rule": _render_horizontal_rule,
    "table": _render_table,
    "task_list": _render_task_list,
    "github_code": _render_github_code,
    "github_notes": _render_github_notes,
}


def blocks_to_html(blocks: List[TextBlock]) -> str:
    """Convert a flat list of TextBlocks into a sequence of HTML fragments.

    Returns the inner HTML (no wrapper) — one fragment per block.
    """
    parts: List[str] = []
    for block in blocks:
        renderer = _BLOCK_RENDERERS.get(block.type, _render_paragraph)
        parts.append(renderer(block))
    return "\n".join(parts)


def build_slides_html(
    blocks: List[TextBlock],
    *,
    css: str = "",
    font_path: Optional[str] = None,
    width: int = 1080,
    height: int = 1080,
) -> str:
    """Build a complete HTML document with slide divs for Playwright rendering.

    Pagination is handled by CSS ``overflow: hidden`` on each slide div
    combined with JavaScript that distributes blocks across slides.

    Args:
        blocks: Flat list of TextBlocks.
        css: CSS stylesheet content to embed.
        font_path: Optional path to a .ttf/.otf font file for @font-face.
        width: Slide width in pixels.
        height: Slide height in pixels.

    Returns:
        Complete HTML string ready for ``page.set_content()``.
    """
    inner_html = blocks_to_html(blocks)

    font_face = ""
    if font_path:
        font_face = f"""
@font-face {{
    font-family: 'CustomFont';
    src: url('file://{font_path}');
}}
body, code, pre {{
    font-family: 'CustomFont', sans-serif;
}}
"""

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
{font_face}
.slide {{
    width: {width}px;
    height: {height}px;
    overflow: hidden;
    position: relative;
    page-break-after: always;
}}
.slide-content {{
    padding: 80px;
}}
.slide.title-slide .slide-content {{
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    height: 100%;
}}
.page-number {{
    position: absolute;
    top: 40px;
    right: 40px;
    width: 48px;
    height: 48px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 18px;
}}
{css}
</style>
</head>
<body>
<div id="content">{inner_html}</div>

<script>
// Paginate content into fixed-size slides
(function() {{
    const content = document.getElementById('content');
    const children = Array.from(content.children);
    content.innerHTML = '';

    const W = {width}, H = {height};
    const PAD = 80; // must match .slide-content padding
    const MAX_CONTENT_H = H - (PAD * 2) - 20; // usable content height
    let slideNum = 0;
    let currentSlide = null;
    let currentContent = null;

    function newSlide(isTitle) {{
        slideNum++;
        currentSlide = document.createElement('div');
        currentSlide.className = 'slide' + (isTitle ? ' title-slide' : '');
        currentSlide.style.width = W + 'px';
        currentSlide.style.height = H + 'px';

        currentContent = document.createElement('div');
        currentContent.className = 'slide-content';
        currentSlide.appendChild(currentContent);

        if (!isTitle) {{
            const pn = document.createElement('div');
            pn.className = 'page-number';
            pn.textContent = slideNum;
            currentSlide.appendChild(pn);
        }}
        content.appendChild(currentSlide);
    }}

    function usedHeight() {{
        // Sum the offset heights of all children in the slide content
        let h = 0;
        for (const child of currentContent.children) {{
            const style = window.getComputedStyle(child);
            h += child.offsetHeight
               + parseInt(style.marginTop || '0')
               + parseInt(style.marginBottom || '0');
        }}
        return h;
    }}

    for (const el of children) {{
        const isTitle = el.tagName === 'H1' && el.classList.contains('title');

        if (isTitle || !currentSlide) {{
            newSlide(isTitle);
        }}

        currentContent.appendChild(el);

        if (usedHeight() > MAX_CONTENT_H) {{
            currentContent.removeChild(el);
            newSlide(false);
            currentContent.appendChild(el);
        }}
    }}
}})();
</script>
</body>
</html>"""
