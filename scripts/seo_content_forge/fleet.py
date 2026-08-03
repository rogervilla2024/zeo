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
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class SiteReport:
    """One site's latest standing derived from its history file.

    Args:
        name: Display name of the site (usually its directory name).
        gates: Gate name to pass/fail from the most recent run.
        scores: Score of every run in history order, latest last.
        previous_gates: Gate name to pass/fail from the run before the
            latest (empty when there is only one run) - regression
            detection compares the two.
    """

    name: str
    gates: dict[str, bool]
    scores: list[int]
    previous_gates: dict[str, bool] = field(default_factory=dict)
    # Design identity from the site's config: "variant | recipe |
    # blocks" for display, and the (recipe, blocks) key two sites must
    # never share. Empty when no site.config.json sat next to the
    # history file or no recipe was recorded.
    combo: str = ""
    combo_key: str = ""

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

    @property
    def regressions(self) -> list[str]:
        """Gates that passed in the previous run and fail now."""
        return sorted(
            gate
            for gate, ok in self.gates.items()
            if not ok and self.previous_gates.get(gate) is True
        )

    @property
    def recoveries(self) -> list[str]:
        """Gates that failed in the previous run and pass now."""
        return sorted(
            gate
            for gate, ok in self.gates.items()
            if ok and self.previous_gates.get(gate) is False
        )

    @property
    def failing(self) -> list[str]:
        """Every failing gate in the latest run."""
        return sorted(gate for gate, ok in self.gates.items() if not ok)


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
    latest = runs[-1]
    if not isinstance(latest, dict):
        raise ValueError(f"{name}: latest run is not a mapping")
    results = latest.get("results")
    if not isinstance(results, dict) or not results:
        raise ValueError(f"{name}: latest run has no results mapping")
    gates = {str(gate): bool(ok) for gate, ok in results.items()}
    scores = [
        sum(bool(ok) for ok in run_results.values())
        for run in runs
        if isinstance(run, dict)
        and isinstance(run_results := run.get("results"), dict)
    ]
    previous_gates: dict[str, bool] = {}
    for run in reversed(runs[:-1]):
        if not isinstance(run, dict):
            continue
        candidate = run.get("results")
        if isinstance(candidate, dict):
            previous_gates = {
                str(gate): bool(ok) for gate, ok in candidate.items()
            }
            break
    return SiteReport(
        name=name, gates=gates, scores=scores, previous_gates=previous_gates
    )


def site_combo(config: dict[str, object]) -> tuple[str, str]:
    """Derive a site's design identity from its parsed config.

    The fleet rule: two sites must never share BOTH the recipe combo
    (``theme.recipe``, e.g. ``"H2+N1+L2+F3"``, recorded by the
    design-theme skill) and the homepage block order
    (``homepage.blocks``; an empty list is the archetype default, so
    the site_type stands in for it).

    Args:
        config: Parsed site.config.json content.

    Returns:
        ``(display, key)`` - a human-readable identity string for the
        report, and the clash-detection key (empty when no recipe is
        recorded, since uniqueness cannot be judged without one).
    """
    theme = config.get("theme")
    theme_map = theme if isinstance(theme, dict) else {}
    variant = str(theme_map.get("variant") or "")
    recipe = str(theme_map.get("recipe") or "")
    homepage = config.get("homepage")
    homepage_map = homepage if isinstance(homepage, dict) else {}
    raw_blocks = homepage_map.get("blocks")
    blocks = raw_blocks if isinstance(raw_blocks, list) else []
    site_type = str(config.get("site_type") or "portal")
    block_part = (
        ">".join(str(block) for block in blocks)
        if blocks
        else f"default:{site_type}"
    )
    display = " | ".join(part for part in (variant, recipe, block_part) if part)
    key = f"{recipe}|{block_part}" if recipe else ""
    return display, key


def combo_clashes(reports: list[SiteReport]) -> list[tuple[str, list[str]]]:
    """Group sites that share a design identity key.

    Args:
        reports: One report per site.

    Returns:
        ``(key, site names)`` pairs for every identity shared by two
        or more sites, sorted by key; empty when the fleet is unique.
    """
    by_key: dict[str, list[str]] = {}
    for report in reports:
        if report.combo_key:
            by_key.setdefault(report.combo_key, []).append(report.name)
    return sorted(
        (key, sorted(names))
        for key, names in by_key.items()
        if len(names) > 1
    )


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


def maintenance_order(reports: list[SiteReport]) -> list[tuple[SiteReport, str]]:
    """Rank the sites that need attention this week, worst first.

    Regressions outrank standing failures (something that USED to work
    just broke - freshest trail, cheapest fix), then total failing
    gates, then the score ratio. Green sites without regressions are
    excluded: the list IS the week's to-do list.

    Args:
        reports: One report per site.

    Returns:
        ``(report, reason)`` pairs, most urgent first; empty when the
        whole fleet is green.
    """
    needy = [r for r in reports if not r.is_green or r.regressions]
    needy.sort(
        key=lambda r: (
            -len(r.regressions),
            -len(r.failing),
            r.score / r.total if r.total else 0.0,
            r.name,
        )
    )
    ranked: list[tuple[SiteReport, str]] = []
    for report in needy:
        parts: list[str] = []
        if report.regressions:
            parts.append(
                f"{len(report.regressions)} regressed: "
                + ", ".join(report.regressions)
            )
        still_failing = [
            gate for gate in report.failing if gate not in report.regressions
        ]
        if still_failing:
            parts.append(
                f"{len(still_failing)} still failing: " + ", ".join(still_failing)
            )
        ranked.append((report, "; ".join(parts) or "regression recovered"))
    return ranked


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
.regressed { outline: 2px solid #dc2626; outline-offset: -2px; }
.recovered { outline: 2px solid #16a34a; outline-offset: -2px; }
.muted { color: #6b7280; }
ol.maintenance { padding-left: 1.4rem; }
ol.maintenance li { margin-bottom: 0.3rem; }
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
    show_combo = any(report.combo for report in reports)

    head = "".join(f"<th>{html.escape(gate)}</th>" for gate in columns)
    rows: list[str] = []
    for report in ordered:
        cells: list[str] = []
        for gate in columns:
            ok = report.gates.get(gate)
            if ok is None:
                cells.append('<td class="muted">-</td>')
            elif not ok and gate in report.regressions:
                cells.append('<td class="fail regressed">FAIL (new)</td>')
            elif ok and gate in report.recoveries:
                cells.append('<td class="pass recovered">PASS (fixed)</td>')
            else:
                cells.append(
                    f'<td class="{"pass" if ok else "fail"}">'
                    f"{'PASS' if ok else 'FAIL'}</td>"
                )
        delta = report.delta
        delta_text = "" if delta is None else f" ({delta:+d})"
        combo_cell = (
            f'<td class="muted">{html.escape(report.combo or "-")}</td>'
            if show_combo
            else ""
        )
        rows.append(
            "<tr>"
            f"<td>{html.escape(report.name)}</td>"
            f"<td>{report.score}/{report.total}{delta_text}</td>"
            + combo_cell
            + "".join(cells)
            + f'<td class="muted">{html.escape(_trend(report.scores))}</td>'
            "</tr>"
        )

    clashes = combo_clashes(reports)
    clash_section = ""
    if clashes:
        clash_items = "\n".join(
            f"<li><strong>{html.escape(', '.join(names))}</strong> share "
            f"<code>{html.escape(key)}</code> - change the recipe combo or "
            "the block order on one of them.</li>"
            for key, names in clashes
        )
        clash_section = (
            "<h2>Identity clashes</h2>\n"
            f'<ol class="maintenance">\n{clash_items}\n</ol>\n'
        )

    ranked = maintenance_order(reports)
    maintenance = ""
    if ranked:
        items = "\n".join(
            f"<li><strong>{html.escape(report.name)}</strong> - "
            f"{html.escape(reason)}</li>"
            for report, reason in ranked
        )
        maintenance = (
            "<h2>Maintenance order</h2>\n"
            f'<ol class="maintenance">\n{items}\n</ol>\n'
        )

    return (
        "<!doctype html>\n"
        '<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{html.escape(title)}</title>\n"
        f"<style>\n{_STYLE}\n</style>\n</head>\n<body>\n"
        f"<h1>{html.escape(title)}</h1>\n"
        f"<p>{len(reports)} site(s), {green} fully green. "
        '"FAIL (new)" regressed since the previous run; '
        '"PASS (fixed)" recovered.</p>\n'
        + clash_section
        + maintenance
        + "<table>\n<thead><tr><th>Site</th><th>Score</th>"
        + ("<th>Identity</th>" if show_combo else "")
        + head
        + "<th>Trend</th></tr></thead>\n<tbody>\n"
        + "\n".join(rows)
        + "\n</tbody>\n</table>\n</body>\n</html>\n"
    )
