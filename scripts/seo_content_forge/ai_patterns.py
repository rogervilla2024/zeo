"""Deterministic linter for AI-tell writing patterns.

The content-humanizer works by judgment; this module is the objective
gate behind it. It flags the phrasings and structural fingerprints that
mark machine-written text, so "humanized" is a measurable state rather
than an opinion:

- banned phrases: formulaic openers, hype words, filler transitions
- structural metrics: sentence-opener repetition and uniform paragraph
  lengths, both of which read as machine rhythm even when no single
  phrase is wrong

Phrase hits are errors (fail the gate); metric breaches are warnings
(reviewer judgment).
"""

from __future__ import annotations

import re
import statistics
from dataclasses import dataclass, field

BANNED_PHRASES: tuple[str, ...] = (
    "in conclusion",
    "in summary",
    "it is important to note",
    "it's important to note",
    "it is worth noting",
    "in today's fast-paced world",
    "in the ever-evolving",
    "delve into",
    "dive into the world of",
    "let's dive in",
    "unlock the power",
    "unlock the potential",
    "game-changer",
    "revolutionize the way",
    "seamlessly integrate",
    "elevate your",
    "harness the power",
    "the world of",
    "look no further",
    "whether you're a",
    "at the end of the day",
    "needless to say",
)
_TRANSITION_OPENERS: tuple[str, ...] = (
    "moreover",
    "furthermore",
    "additionally",
    "however",
    "therefore",
)


@dataclass(slots=True)
class PhraseFinding:
    """One banned-phrase occurrence.

    Args:
        line: One-based line number in the article.
        phrase: The banned phrase that matched.
        context: The matching line, trimmed.
    """

    line: int
    phrase: str
    context: str


@dataclass(slots=True)
class PatternReport:
    """Outcome of linting one article.

    Args:
        findings: Banned-phrase occurrences (errors).
        warnings: Structural-metric breaches (reviewer judgment).
    """

    findings: list[PhraseFinding] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        """Return ``True`` when no banned phrase was found."""
        return not self.findings


def _sentences(text: str) -> list[str]:
    """Split prose into sentences, ignoring markdown structure and code."""
    prose_lines: list[str] = []
    in_code = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code or not stripped:
            continue
        if stripped.startswith(("#", ">", "|", "![")):
            continue
        prose_lines.append(line)
    raw = re.split(r"(?<=[.!?])\s+", " ".join(prose_lines))
    return [sentence.strip() for sentence in raw if len(sentence.split()) >= 3]


def analyze(markdown: str) -> PatternReport:
    """Lint an article for AI-tell patterns.

    Args:
        markdown: The article body.

    Returns:
        A :class:`PatternReport` with findings and warnings.
    """
    report = PatternReport()

    for index, line in enumerate(markdown.splitlines(), start=1):
        lowered = line.lower()
        for phrase in BANNED_PHRASES:
            if phrase in lowered:
                report.findings.append(
                    PhraseFinding(line=index, phrase=phrase, context=line.strip())
                )

    sentences = _sentences(markdown)
    if len(sentences) >= 10:
        openers = [sentence.split()[0].lower().strip(",;:") for sentence in sentences]
        most_common = max(set(openers), key=openers.count)
        ratio = openers.count(most_common) / len(openers)
        if ratio > 0.2:
            report.warnings.append(
                f"sentence opener {most_common!r} starts {ratio:.0%} of "
                "sentences; vary sentence openings"
            )
        transition_count = sum(1 for opener in openers if opener in _TRANSITION_OPENERS)
        if transition_count / len(sentences) > 0.1:
            report.warnings.append(
                f"{transition_count} of {len(sentences)} sentences open with "
                "a formulaic transition; cut or rephrase most of them"
            )

    paragraphs = [
        len(paragraph.split())
        for paragraph in re.split(r"\n\s*\n", markdown)
        if len(paragraph.split()) >= 20 and not paragraph.strip().startswith("#")
    ]
    if len(paragraphs) >= 5:
        spread = statistics.pstdev(paragraphs) / statistics.mean(paragraphs)
        if spread < 0.25:
            report.warnings.append(
                "paragraph lengths are unnaturally uniform "
                f"(relative spread {spread:.2f}); vary paragraph size"
            )

    return report
