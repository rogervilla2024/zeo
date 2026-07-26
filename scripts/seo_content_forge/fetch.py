"""Minimal HTTP fetch helper for the checker CLIs.

Uses only the standard library so the package stays dependency-light.
Proxy settings are honored automatically from the environment
(``HTTPS_PROXY``), which matters in sandboxed and CI environments.
"""

from __future__ import annotations

import logging
import re
import urllib.error
import urllib.request
from dataclasses import dataclass

logger = logging.getLogger(__name__)

_USER_AGENT = "seo-content-forge/0.2 (+https://github.com/seo-content-forge)"


def decode_body(body: bytes, content_type: str) -> str:
    """Decode a response body honoring the Content-Type charset.

    Endpoints that ignore UTF-8 defaults (e.g. Google Suggest answers
    in ISO-8859-9 for ``hl=tr`` unless ``oe=utf-8`` is sent) would
    otherwise turn every non-ASCII character into U+FFFD and silently
    corrupt downstream text.

    Args:
        body: Raw response bytes.
        content_type: The Content-Type header value (any case).

    Returns:
        The decoded text; falls back to UTF-8 with replacement when the
        declared charset is missing or unknown.
    """
    match = re.search(r"charset=[\"']?([\w.-]+)", content_type, re.IGNORECASE)
    if match:
        try:
            return body.decode(match.group(1), errors="replace")
        except LookupError:
            logger.warning("unknown charset %r; falling back to utf-8", match.group(1))
    return body.decode("utf-8", errors="replace")


@dataclass(slots=True)
class FetchResult:
    """Outcome of one HTTP GET.

    Args:
        status: HTTP status code, or 0 when the request failed entirely.
        content_type: Value of the Content-Type header, lowercased.
        text: Decoded body (empty on failure).
    """

    status: int
    content_type: str
    text: str

    @property
    def ok(self) -> bool:
        """Return ``True`` for a 2xx response."""
        return 200 <= self.status < 300


def fetch(
    url: str,
    accept: str = "*/*",
    timeout: float = 20.0,
    headers: dict[str, str] | None = None,
) -> FetchResult:
    """Fetch a URL and return status, content type, and body text.

    Args:
        url: Absolute http(s) URL.
        accept: Value for the Accept request header (used for markdown
            content negotiation probing).
        timeout: Socket timeout in seconds.
        headers: Extra request headers (e.g. Authorization).

    Returns:
        A :class:`FetchResult`. Network-level failures are reported as
        ``status=0`` rather than raised, so callers can treat "missing"
        and "unreachable" uniformly.
    """
    request_headers = {"User-Agent": _USER_AGENT, "Accept": accept}
    if headers:
        request_headers.update(headers)
    request = urllib.request.Request(url, headers=request_headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body: bytes = response.read()
            content_type = str(response.headers.get("Content-Type", "")).lower()
            return FetchResult(
                status=int(response.status),
                content_type=content_type,
                text=decode_body(body, content_type),
            )
    except urllib.error.HTTPError as exc:
        return FetchResult(status=int(exc.code), content_type="", text="")
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        logger.error("fetch failed for %s: %s", url, exc)
        return FetchResult(status=0, content_type="", text="")
