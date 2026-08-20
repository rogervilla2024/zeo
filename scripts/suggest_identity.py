"""CLI to propose fleet-unique design identities for the next site.

Usage:
    python suggest_identity.py --scan ~/sites --count 3
    python suggest_identity.py --config ~/sites/blog/site.config.json \
        --config ~/sites/docs/site.config.json

The inverse of fleet_report.py's identity-clash check: instead of
flagging two sites that already collide, it reads the fleet's
site.config.json files and answers "what should the NEXT site wear?"
- a variant nobody uses, an anatomy and recipe combo with fresh
letters, an unused type pairing and finish, and a primary hue band
the fleet does not own yet. Each suggestion prints the theme.recipe
string and the config keys to paste. Deterministic for a given
fleet.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import orjson

from seo_content_forge.identity import fleet_usage, suggest


def _load_configs(paths: list[Path]) -> tuple[list[dict[str, object]], int]:
    configs: list[dict[str, object]] = []
    skipped = 0
    for path in paths:
        try:
            parsed = orjson.loads(path.read_bytes())
        except (OSError, orjson.JSONDecodeError) as exc:
            print(f"SKIP {path}: {exc}", file=sys.stderr)
            skipped += 1
            continue
        if isinstance(parsed, dict):
            configs.append(parsed)
    return configs, skipped


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns 0 on success, 2 on unusable input."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scan",
        type=Path,
        help="Directory with one subdirectory per site; picks up each "
        "<site>/site.config.json.",
    )
    parser.add_argument(
        "--config",
        action="append",
        type=Path,
        default=[],
        help="Add one site.config.json explicitly (repeatable).",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=3,
        help="How many identities to suggest (default: 3).",
    )
    args = parser.parse_args(argv)

    paths: list[Path] = []
    if args.scan:
        scan = args.scan.expanduser()
        if not scan.is_dir():
            print(f"Not a directory: {scan}", file=sys.stderr)
            return 2
        for sub in sorted(scan.iterdir()):
            candidate = sub / "site.config.json"
            if candidate.is_file():
                paths.append(candidate)
    paths.extend(path.expanduser() for path in args.config)

    configs, _ = _load_configs(paths)
    usage = fleet_usage(configs)
    print(
        f"Fleet: {len(configs)} site(s); "
        f"{len(usage.variants)} variant(s), "
        f"{len(usage.letters)} recipe letter(s), "
        f"{len(usage.hue_bands)}/12 hue band(s) in use."
    )

    for number, pick in enumerate(suggest(configs, args.count), start=1):
        finish = pick.finish or "flat"
        print(
            f"\n{number}. variant={pick.variant}  finish={finish}  "
            f"primary={pick.primary} (hue band {pick.hue_band})"
        )
        print(f"   recipe: {pick.recipe}")
        print(
            '   config: "theme": {'
            f'"variant": "{pick.variant}", "finish": "{pick.finish}", '
            f'"recipe": "{pick.recipe}", '
            f'"palette": {{"primary": "{pick.primary}"}}}}'
        )
    print(
        "\nTune the primary toward the niche (same hue band), then run "
        "check_contrast.py and fleet_report.py as usual."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
