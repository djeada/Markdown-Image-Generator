"""Inline GitHub file URLs found in TextBlocks.

Scans paragraph TextBlocks for standalone GitHub blob URLs like:
    https://github.com/user/repo/blob/branch/path/to/file.py

Fetches the raw file content and replaces the paragraph with a
``github_code`` or ``github_notes`` TextBlock whose ``data`` is a
JSON-encoded payload containing the file metadata and content.

The HTML builder renders these as styled file cards.
"""

import json
import logging
import re
from pathlib import PurePosixPath
from typing import List, Optional
from urllib.error import URLError
from urllib.request import Request, urlopen

from src.data.text_block import TextBlock

logger = logging.getLogger(__name__)

# Matches a GitHub blob URL (full line or inside a markdown link)
_GITHUB_BLOB_RE = re.compile(
    r"(?:\[.*?\]\()?"
    r"https://github\.com/"
    r"(?P<owner>[^/]+)/"
    r"(?P<repo>[^/]+)/"
    r"blob/"
    r"(?P<ref>[^/]+)/"
    r"(?P<path>.+?)"
    r"\)?"
    r"\s*$",
)

# Map file suffix → language label for display
LANG_MAP = {
    ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
    ".jsx": "JSX", ".tsx": "TSX", ".java": "Java",
    ".c": "C", ".cpp": "C++", ".h": "C", ".hpp": "C++",
    ".cs": "C#", ".go": "Go", ".rs": "Rust",
    ".rb": "Ruby", ".php": "PHP", ".swift": "Swift",
    ".kt": "Kotlin", ".scala": "Scala",
    ".sh": "Bash", ".bash": "Bash", ".zsh": "Zsh",
    ".sql": "SQL", ".r": "R",
    ".json": "JSON", ".yaml": "YAML", ".yml": "YAML",
    ".toml": "TOML", ".xml": "XML", ".html": "HTML",
    ".css": "CSS", ".scss": "SCSS",
    ".dockerfile": "Dockerfile",
}

_MARKDOWN_EXTENSIONS = {".md", ".markdown", ".mdown", ".mkd", ".rst", ".txt"}

_REQUEST_TIMEOUT = 15


def _github_raw_url(owner: str, repo: str, ref: str, path: str) -> str:
    """Convert GitHub blob URL components to a raw.githubusercontent.com URL."""
    return f"https://raw.githubusercontent.com/{owner}/{repo}/{ref}/{path}"


def _fetch_url(url: str) -> Optional[str]:
    """Fetch a URL and return text content, or None on failure."""
    try:
        req = Request(url, headers={"User-Agent": "Markdown-Image-Generator"})
        with urlopen(req, timeout=_REQUEST_TIMEOUT) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except (URLError, OSError, UnicodeDecodeError) as exc:
        logger.warning("Failed to fetch %s: %s", url, exc)
        return None


def _is_github_url_block(block: TextBlock) -> bool:
    """Check if a paragraph TextBlock contains only a GitHub blob URL."""
    if block.type != "paragraph":
        return False
    return bool(_GITHUB_BLOB_RE.match(block.data.strip()))


def _make_payload(owner: str, repo: str, ref: str, path: str, content: str) -> str:
    """Encode file metadata + content as JSON for the TextBlock data field."""
    suffix = PurePosixPath(path).suffix.lower()
    return json.dumps({
        "owner": owner,
        "repo": repo,
        "ref": ref,
        "path": path,
        "filename": PurePosixPath(path).name,
        "language": LANG_MAP.get(suffix, suffix.lstrip(".").upper() or "Text"),
        "content": content,
    }, ensure_ascii=False)


def inline_github_urls(blocks: List[TextBlock]) -> List[TextBlock]:
    """Replace paragraph blocks containing GitHub URLs with rich file blocks.

    Args:
        blocks: Flat list of TextBlocks from the parser.

    Returns:
        New list with GitHub URL paragraphs replaced by ``github_code``
        or ``github_notes`` TextBlocks.
    """
    result: List[TextBlock] = []

    for block in blocks:
        if not _is_github_url_block(block):
            result.append(block)
            continue

        m = _GITHUB_BLOB_RE.match(block.data.strip())
        if not m:
            result.append(block)
            continue

        owner, repo, ref, path = (
            m.group("owner"), m.group("repo"), m.group("ref"), m.group("path"),
        )
        raw_url = _github_raw_url(owner, repo, ref, path)
        logger.info("Fetching GitHub file: %s/%s/%s", owner, repo, path)

        content = _fetch_url(raw_url)
        if content is None:
            result.append(block)
            continue

        suffix = PurePosixPath(path).suffix.lower()
        payload = _make_payload(owner, repo, ref, path, content)

        if suffix in _MARKDOWN_EXTENSIONS:
            result.append(TextBlock("github_notes", payload))
        else:
            result.append(TextBlock("github_code", payload))

    return result
