"""
Tests for chunking and retrieval scoring.
"""
from app.retrieval.chunking import chunk_transcript, parse_speaker_turns
from app.retrieval.search import hybrid_search


def test_chunker_basic():
    sample_text = """---
title: "Testing Growth"
guest: "Adam Fishman"
---
Adam Fishman (00:00:10):
Welcome to the podcast. Today we talk about growth loops and retention metrics.

Lenny (00:00:25):
That is fantastic. How do you scale teams?
"""
    parsed = chunk_transcript("test.md", sample_text, target_chunk_words=10)
    assert parsed.title == "Testing Growth"
    assert parsed.guest == "Adam Fishman"
    assert len(parsed.chunks) >= 1
    assert any("growth" in c.text.lower() for c in parsed.chunks)


from app.retrieval.search import STOPWORDS, lexical_score


def test_lexical_stopword_filtering():
    # Verify common stop words are present in STOPWORDS set
    assert "how" in STOPWORDS
    assert "do" in STOPWORDS
    assert "i" in STOPWORDS
    assert "cake" not in STOPWORDS
    assert "chocolate" not in STOPWORDS

    # Verify score with only stopwords is zero
    score = lexical_score("how do I", "some text", "Guest", "Title")
    assert score == 0.0
