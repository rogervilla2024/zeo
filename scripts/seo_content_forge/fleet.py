"""Aggregate per-site seo_report histories into one fleet view.

Each site tracked with :mod:`seo_report` accumulates a
``.seo-history.json`` file (a list of runs, each with a ``results``
mapping of gate name to pass/fail and a ``score``). This module folds
any number of those histories into one summary and renders it as a
self-contained HTML dashboard, so a portfolio is reviewed on one page
instead of site by site.
"""

from __future__ import annotations

import html
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class SiteReport:
    """One site's latest standing derived from its history file.

    Args:
        name: Display name of the site (usually its directory name).
        gates: Gate name to pass/fail from the most recent run.
        scores: Score of every run in history order, latest last.
    """

    name: str
    gates: dict[str, bool]
    scores: list[int]

    @property
    def score(self) -> int:
        """Gates passed in the latest run."""
        return sum(self.gates.values())

    @property
    def total(self) -> int:
        """Gates measured in the latest run."""
        return len(self.gates)

    @property
    def delta(self) -> int | None:
        """Score change against the previous run, if there was one."""
        if len(self.scores) < 2:
            return None
        return self.scores[-1] - self.scores[-2]

    @property
    def is_green(self) -> bool:
        """True when every gate in the latest run passed."""
        return self.total > 0 and all(self.gates.values())


def site_report(name: str, runs: list[dict[str, object]]) -> SiteReport:
    """Fold one parsed history file into a :class:`SiteReport`.

    Args:
        name: Display name for the site.
        runs: Parsed ``.seo-history.json`` content, oldest run first.

    Returns:
        The site's report.

    Raises:
        ValueError: If ``runs`` is empty or the latest run has no
            ``results`` mapping.
    """
    if not runs:
        raise ValueError(f"{name}: history is empty")
    results = runs[-1].get("results")
    if not isinstance(results, dict) or not results:
        raise ValueError(f"{name}: latest run has no results mapping")
    gates = {str(gate): bool(ok) for gate, ok in results.items()}
    scores = [
        sum(run_results.values())
        for run in runs
        if isinstance(run_results := run.get("results"), dict)
    ]
    return SiteReport(name=name, gates=gates, scores=scores)


def discover(root: Path) -> dict[str, Path]:
    """Find ``.seo-history.json`` files one level below ``root``.

    Args:
        root: Directory holding one subdirectory per site.

    Returns:
        Site name (subdirectory name) to history file path, sorted by
        name.
    """
    return {
        path.parent.name: path
        for path in sorted(root.glob("*/.seo-history.json"))
        if path.is_file()
    }


def gate_columns(reports: list[SiteReport]) -> list[str]:
    """Union of gate names across reports, in first-appearance order."""
    columns: list[str] = []
    for report in reports:
        for gate in report.gates:
            if gate not in columns:
                columns.append(gate)
    return columns


def _trend(scores: list[int]) -> str:
    """Render the score trail of the last runs as plain text."""
    return " ".join(str(score) for score in scores[-8:])


_STYLE = """
body { font-family: system-ui, sans-serif; margin: 2rem auto;
       max-width: 72rem; padding: 0 1rem; color: #111827; }
h1 { font-size: 1.5rem; }
table { border-collapse: collapse; width: 100%; }
th, td { border: 1px solid #d1d5db; padding: 0.4rem 0.6rem;
         text-align: left; font-size: 0.9rem; }
th { background: #f6f8fa; }
.pass { background: #dcfce7; }
.fail { background: #fee2e2; font-weight: 600; }
.muted { color: #6b7280; }
""".strip()


def build_html(reports: list[SiteReport], title: str = "Fleet SEO report") -> str:
    """Render the fleet summary as a self-contained HTML page.

    Args:
        reports: One report per site; rendered worst score ratio first.
        title: Page title.

    Returns:
        Complete HTML document as a string.
    """
    ordered = sorted(reports, key=lambda r: (r.score / r.total if r.total else 0.0))
    columns = gate_columns(ordered)
    green = sum(report.is_green for report in reports)

    head = "".join(f"<th>{html.escape(gate)}</th>" for gate in columns)
    rows: list[str] = []
    for report in ordered:
        cells: list[str] = []
        for gate in columns:
            ok = report.gates.get(gate)
            if ok is None:
                cells.append('<td class="muted">-</td>')
            else:
                cells.append(
                    f'<td class="{"pass" if ok else "fail"}">'
                    f"{'PASS' if ok else 'FAIL'}</td>"
                )
        delta = report.delta
        delta_text = "" if delta is None else f" ({delta:+d})"
        rows.append(
            "<tr>"
            f"<td>{html.escape(report.name)}</td>"
            f"<td>{report.score}/{report.total}{delta_text}</td>"
            + "".join(cells)
            + f'<td class="muted">{html.escape(_trend(report.scores))}</td>'
            "</tr>"
        )

    return (
        "<!doctype html>\n"
        '<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{html.escape(title)}</title>\n"
        f"<style>\n{_STYLE}\n</style>\n</head>\n<body>\n"
        f"<h1>{html.escape(title)}</h1>\n"
        f"<p>{len(reports)} site(s), {green} fully green.</p>\n"
        "<table>\n<thead><tr><th>Site</th><th>Score</th>"
        + head
        + "<th>Trend</th></tr></thead>\n<tbody>\n"
        + "\n".join(rows)
        + "\n</tbody>\n</table>\n</body>\n</html>\n"
    )
