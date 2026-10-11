"""
Hybrid search engine combining vector cosine similarity + lexical keyword search
merged via Reciprocal Rank Fusion (RRF).
Includes threshold cutoff for refusal mode ("the transcripts don't cover this").
"""
import math
import re
from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Chunk, Document
from app.retrieval.embeddings import embedding_client
from app.config import settings
from app.logging import logger


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm_v1 = math.sqrt(sum(a * a for a in v1))
    norm_v2 = math.sqrt(sum(b * b for b in v2))
    if norm_v1 == 0.0 or norm_v2 == 0.0:
        return 0.0
    return dot_product / (norm_v1 * norm_v2)


STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "as", "at",
    "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can", "did", "do",
    "does", "doing", "don", "down", "during", "each", "few", "for", "from", "further", "had", "has", "have",
    "having", "he", "her", "here", "hers", "herself", "him", "himself", "his", "how", "i", "if", "in", "into",
    "is", "it", "its", "itself", "just", "me", "more", "most", "my", "myself", "no", "nor", "not", "now", "of",
    "off", "on", "once", "only", "or", "other", "our", "ours", "ourselves", "out", "over", "own", "s", "same",
    "she", "should", "so", "some", "such", "t", "than", "that", "the", "their", "theirs", "them", "themselves",
    "then", "there", "these", "they", "this", "those", "through", "to", "too", "under", "until", "up", "very",
    "was", "we", "were", "what", "when", "where", "which", "while", "who", "whom", "why", "will", "with", "you"
}


def lexical_score(query: str, text: str, guest: str, title: str) -> float:
    """Computes BM25-style lexical keyword and entity overlap score with stopword filtering."""
    raw_tokens = re.findall(r"\w+", query.lower())
    query_tokens = [t for t in raw_tokens if t not in STOPWORDS and len(t) > 1]
    if not query_tokens:
        return 0.0

    text_words = set(re.findall(r"\w+", text.lower()))
    guest_words = set(re.findall(r"\w+", guest.lower()))
    title_words = set(re.findall(r"\w+", title.lower()))

    score = 0.0
    for token in query_tokens:
        # Boost guest name matches heavily (e.g. "Adam Fishman", "Elena Verna")
        if token in guest_words:
            score += 4.0
        if token in title_words:
            score += 2.0
        # Check text match
        if token in text_words:
            count = len(re.findall(r"\b" + re.escape(token) + r"\b", text.lower()))
            if count > 0:
                score += 1.0 + math.log(count)

    return score


class SearchResult:
    def __init__(
        self,
        chunk_id: str,
        document_id: str,
        guest: str,
        title: str,
        youtube_url: Optional[str],
        start_ref: str,
        speaker: str,
        text: str,
        vector_score: float,
        lexical_score: float,
        rrf_score: float,
    ):
        self.chunk_id = chunk_id
        self.document_id = document_id
        self.guest = guest
        self.title = title
        self.youtube_url = youtube_url
        self.start_ref = start_ref
        self.speaker = speaker
        self.text = text
        self.vector_score = vector_score
        self.lexical_score = lexical_score
        self.rrf_score = rrf_score

    def to_citation_dict(self) -> Dict[str, Any]:
        return {
            "guest": self.guest,
            "episode_title": self.title,
            "timestamp": self.start_ref,
            "youtube_url": self.youtube_url,
            "quote_snippet": self.text[:180] + "..." if len(self.text) > 180 else self.text
        }


class HybridSearchEngine:
    async def search(
        self,
        query: str,
        session: AsyncSession,
        top_k: int = 6,
        rrf_k: int = 60
    ) -> Tuple[List[SearchResult], bool]:
        """
        Executes hybrid search and returns (results, is_covered).
        is_covered is False if the maximum relevance score falls below threshold.
        """
        # 1. Generate query embedding
        query_embedding = await embedding_client.get_embedding(query)

        # 2. Fetch candidate chunks joined with document metadata
        stmt = select(Chunk, Document).join(Document, Chunk.document_id == Document.id)
        res = await session.execute(stmt)
        rows = res.all()

        if not rows:
            logger.warning("no_chunks_found_in_database")
            return [], False

        # 3. Compute vector and lexical rankings
        scored_candidates = []
        for chunk, doc in rows:
            v_score = 0.0
            if chunk.embedding and query_embedding:
                v_score = cosine_similarity(query_embedding, chunk.embedding)
            
            l_score = lexical_score(query, chunk.text, doc.guest, doc.title)

            scored_candidates.append({
                "chunk": chunk,
                "doc": doc,
                "v_score": v_score,
                "l_score": l_score,
            })

        # Rank by vector score
        scored_candidates.sort(key=lambda x: x["v_score"], reverse=True)
        for rank, item in enumerate(scored_candidates):
            item["vector_rank"] = rank + 1

        # Rank by lexical score
        scored_candidates.sort(key=lambda x: x["l_score"], reverse=True)
        for rank, item in enumerate(scored_candidates):
            item["lexical_rank"] = rank + 1

        # 4. Compute Reciprocal Rank Fusion (RRF) score
        results: List[SearchResult] = []
        for item in scored_candidates:
            v_rank = item["vector_rank"]
            l_rank = item["lexical_rank"]
            rrf = (1.0 / (rrf_k + v_rank)) + (1.0 / (rrf_k + l_rank))

            chunk = item["chunk"]
            doc = item["doc"]
            results.append(SearchResult(
                chunk_id=chunk.id,
                document_id=doc.id,
                guest=doc.guest,
                title=doc.title,
                youtube_url=doc.source_url,
                start_ref=chunk.start_ref or "00:00:00",
                speaker=chunk.speaker or doc.guest,
                text=chunk.text,
                vector_score=item["v_score"],
                lexical_score=item["l_score"],
                rrf_score=rrf,
            ))

        # Sort by RRF score descending
        results.sort(key=lambda x: x.rrf_score, reverse=True)
        top_results = results[:top_k]

        # 5. Check threshold cutoff for refusal
        # If top vector score < 0.40 and top lexical score < 2.0, the topic is not covered
        max_v = max((r.vector_score for r in top_results), default=0.0)
        max_l = max((r.lexical_score for r in top_results), default=0.0)

        is_covered = (max_v >= 0.42 or max_l >= 2.5)

        logger.info(
            "hybrid_search_completed",
            query=query[:60],
            top_vector_score=round(max_v, 3),
            top_lexical_score=round(max_l, 3),
            is_covered=is_covered
        )

        return top_results, is_covered


hybrid_search = HybridSearchEngine()
