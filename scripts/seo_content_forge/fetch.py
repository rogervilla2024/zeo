"""Minimal HTTP fetch helper for the checker CLIs.

Uses only the standard library so the package stays dependency-light.
Proxy settings are honored automatically from the environment
(``HTTPS_PROXY``), which matters in sandboxed and CI environments.
"""

from __future__ import annotations

import logging
import urllib.error
import urllib.request
from dataclasses import dataclass

logger = logging.getLogger(__name__)

_USER_AGENT = "seo-content-forge/0.2 (+https://github.com/seo-content-forge)"


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


def fetch(url: str, accept: str = "*/*", timeout: float = 20.0) -> FetchResult:
    """Fetch a URL and return status, content type, and body text.

    Args:
        url: Absolute http(s) URL.
        accept: Value for the Accept request header (used for markdown
            content negotiation probing).
        timeout: Socket timeout in seconds.

    Returns:
        A :class:`FetchResult`. Network-level failures are reported as
        ``status=0`` rather than raised, so callers can treat "missing"
        and "unreachable" uniformly.
    """
    request = urllib.request.Request(
        url, headers={"User-Agent": _USER_AGENT, "Accept": accept}
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body: bytes = response.read()
            return FetchResult(
                status=int(response.status),
                content_type=str(response.headers.get("Content-Type", "")).lower(),
                text=body.decode("utf-8", errors="replace"),
            )
    except urllib.error.HTTPError as exc:
        return FetchResult(status=int(exc.code), content_type="", text="")
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        logger.error("fetch failed for %s: %s", url, exc)
        return FetchResult(status=0, content_type="", text="")
