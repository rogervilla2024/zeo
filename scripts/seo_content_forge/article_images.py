"""Article image completeness checks over a content collection.

The publishing pipeline mandates a hero image plus a minimum number of
body images per article (site.config.json ``images.min``), but a
skipped step used to go unnoticed: the offline gates only looked at the
built HTML, where an imageless article is still valid markup. This
module checks the source of truth - the markdown files' frontmatter and
bodies - so a forgotten image fails the score card instead of shipping.
"""

from __future__ import annotations

import re
from pathlib import Path

_BODY_IMAGE = re.compile(r"!\[|<img\b", re.IGNORECASE)


def parse_frontmatter(text: str) -> dict[str, str]:
    """Extract top-level scalar frontmatter fields from markdown.

    A deliberately small YAML subset - ``key: value`` lines between the
    leading ``---`` fences - because the gate only needs ``image``.
    Nested/list entries (indented or ``-`` lines) are skipped.

    Args:
        text: Full markdown file content.

    Returns:
        Mapping of top-level keys to their unquoted string values;
        empty when the file has no frontmatter block.
    """
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    fields: dict[str, str] = {}
    for line in text[3:end].splitlines():
        if not line or line[0] in " \t#-":
            continue
        key, sep, value = line.partition(":")
        if not sep:
            continue
        fields[key.strip()] = value.strip().strip("\"'")
    return fields


def body_image_count(text: str) -> int:
    """Count images in the article body (markdown ``![`` or ``<img``).

    Args:
        text: Full markdown file content; the frontmatter block is
            excluded so a hero path in frontmatter never counts.

    Returns:
        Number of body image occurrences.
    """
    body = text
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            body = text[end + 4 :]
    return len(_BODY_IMAGE.findall(body))


def check_articles(content_dir: Path, min_body_images: int) -> list[str]:
    """Find image-policy violations across a content collection.

    Args:
        content_dir: Directory of article markdown files (searched
            recursively for ``*.md``).
        min_body_images: Required in-body image count per article
            (``images.min`` from site.config.json; 0 disables it).

    Returns:
        Human-readable problems, one per violation, sorted by file.
        Empty when every article satisfies the policy.
    """
    problems: list[str] = []
    for path in sorted(content_dir.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        if not parse_frontmatter(text).get("image"):
            problems.append(f"{path.name}: missing hero image frontmatter")
        count = body_image_count(text)
        if count < min_body_images:
            problems.append(
                f"{path.name}: {count} body image(s), "
                f"config requires at least {min_body_images}"
            )
    return problems
