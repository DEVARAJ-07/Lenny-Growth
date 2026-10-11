"""
Tests for Ship 30 essay validator.
"""
from app.agent.skills.ship30.validator import ship30_validator


def test_ship30_validator_scoring():
    sample_essay = """# The Real Reason Your Retention Is Flat (And How to Fix It)

Most product leaders make the same costly mistake: they optimize onboarding before understanding activation.
When users drop off on day 3, founders panic and redesign the signup screen.

## Why Early Churn Is an Activation Failure

As Adam Fishman noted on Lenny's Podcast (00:14:22), activation is not a single button click.
It is the realization of promised value before cognitive fatigue sets in.

- Step 1: Identify the aha moment
- Step 2: Strip out extraneous form fields
- Step 3: Guide users to value in under 2 minutes

## The Tactical Monday Morning Checklist

Here is what operators must implement immediately:
1. Audit your time-to-first-value metric.
2. Remove any verification step that blocks initial usage.
3. Align product instrumentation with user success milestones.
"""
    report = ship30_validator.validate(sample_essay)
    assert report.word_count > 50
    assert report.score > 0.4
    assert any("word count" in f.lower() or "hook" in f.lower() or "citation" in f.lower() for f in report.feedback)
