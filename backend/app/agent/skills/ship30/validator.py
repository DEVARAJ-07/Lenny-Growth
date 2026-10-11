"""
Ship 30 for 30 Structure & Word-Count Validator.
"""
import re
from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class ValidationReport:
    is_valid: bool
    word_count: int
    has_hook: bool
    has_subheadings: bool
    has_bullets: bool
    has_bolding: bool
    has_takeaway: bool
    has_citations: bool
    score: float
    feedback: List[str]


class Ship30Validator:
    def validate(self, text: str) -> ValidationReport:
        words = text.split()
        word_count = len(words)
        feedback = []

        # 1. Word count check (target ~1,250 words)
        count_valid = (word_count >= 800)
        if word_count < 800:
            feedback.append(f"Word count ({word_count}) is below minimum target of 800-1,250 words.")
        elif word_count > 1600:
            feedback.append(f"Word count ({word_count}) exceeds upper limit of ~1,400 words.")

        # 2. Hook check (starts with # Header or strong lead)
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        has_hook = False
        if lines and (lines[0].startswith("#") or len(lines[0]) > 20):
            has_hook = True
        else:
            feedback.append("Missing strong opening hook or headline.")

        # 3. Subheadings (H2 or H3)
        h2_h3_count = len(re.findall(r"^#{2,3}\s+", text, re.MULTILINE))
        has_subheadings = h2_h3_count >= 3
        if not has_subheadings:
            feedback.append(f"Found only {h2_h3_count} subheadings; Ship 30 requires at least 3-5 subheadings.")

        # 4. Bullet points
        bullet_count = len(re.findall(r"^\s*[\*\-\•]\s+", text, re.MULTILINE))
        has_bullets = bullet_count >= 3
        if not has_bullets:
            feedback.append("Insufficient bullet points for skimmability.")

        # 5. Selective bold emphasis
        bold_matches = re.findall(r"\*\*[^*]+\*\*", text)
        has_bolding = len(bold_matches) >= 3
        if not has_bolding:
            feedback.append("Missing selective bold emphasis for skimmable reading.")

        # 6. Specific Takeaway
        has_takeaway = bool(re.search(r"(takeaway|summary|action item|playbook|key takeaway|what to do)", text, re.IGNORECASE))
        if not has_takeaway:
            feedback.append("Missing clear actionable takeaway or conclusion.")

        # 7. Grounding citations / Guest mentions
        citation_matches = re.findall(r"\([0-9]{2}:[0-9]{2}:[0-9]{2}\)|according to|podcast|episode", text, re.IGNORECASE)
        has_citations = len(citation_matches) >= 1
        if not has_citations:
            feedback.append("No transcript episode or timestamp citations detected.")

        checks = [
            count_valid,
            has_hook,
            has_subheadings,
            has_bullets,
            has_bolding,
            has_takeaway,
            has_citations
        ]
        score = sum(1.0 for c in checks if c) / len(checks)
        is_valid = score >= 0.70

        return ValidationReport(
            is_valid=is_valid,
            word_count=word_count,
            has_hook=has_hook,
            has_subheadings=has_subheadings,
            has_bullets=has_bullets,
            has_bolding=has_bolding,
            has_takeaway=has_takeaway,
            has_citations=has_citations,
            score=round(score, 2),
            feedback=feedback
        )


ship30_validator = Ship30Validator()
