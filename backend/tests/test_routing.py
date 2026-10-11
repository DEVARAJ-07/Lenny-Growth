"""
Tests for Agent Router classification.
"""
from app.agent.router import agent_router


def test_classify_ship30():
    queries = [
        "Write a Ship 30 essay on product-market fit",
        "Generate an atomic essay about onboarding metrics",
        "Ship 30 for 30 essay about retention loops",
    ]
    for q in queries:
        assert agent_router.classify(q) == "ship30"


def test_classify_artifact():
    queries = [
        "Create an interactive dashboard in HTML",
        "Build a component showing CAC and LTV metrics",
        "Generate a tool to calculate conversion rates with HTML/CSS",
    ]
    for q in queries:
        assert agent_router.classify(q) == "artifact"


def test_classify_question():
    queries = [
        "What does Adam Fishman say about growth teams?",
        "How should early-stage startups evaluate churn?",
        "What are the best practices for user research?",
    ]
    for q in queries:
        assert agent_router.classify(q) == "question"
