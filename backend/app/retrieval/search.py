"""
Hybrid search engine combining vector cosine similarity + lexical keyword search
merged via Reciprocal Rank Fusion (RRF).
High-performance in-memory cached vector index with NumPy acceleration.
Includes threshold cutoff for refusal mode ("the transcripts don't cover this").
"""
import os
import json
import math
import re
import sqlite3
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from app.retrieval.embeddings import embedding_client
from app.config import settings
from app.logging import logger


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
    def __init__(self):
        self.matrix: Optional[np.ndarray] = None
        self.metadata: List[Dict[str, Any]] = []
        self._initialized = False

    def _ensure_index_loaded(self):
        """Loads cached in-memory NumPy vector matrix and metadata, or builds from SQLite."""
        if self._initialized:
            return

        cache_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data")
        npz_file = os.path.join(cache_dir, "search_index.npz")
        meta_file = os.path.join(cache_dir, "search_metadata.json")

        if os.path.exists(npz_file) and os.path.exists(meta_file):
            try:
                data = np.load(npz_file)
                self.matrix = data["matrix"]
                with open(meta_file, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)
                self._initialized = True
                logger.info("vector_search_cache_loaded", total_chunks=len(self.metadata))
                return
            except Exception as e:
                logger.warning("failed_to_load_vector_cache", error=str(e))

        # Fallback to loading from SQLite lenny_growth.db
        db_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "lenny_growth.db")
        if not os.path.exists(db_path):
            db_path = "lenny_growth.db"

        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            rows = conn.execute("""
                SELECT c.id, c.document_id, c.start_ref, c.speaker, c.text, c.embedding, d.guest, d.title, d.source_url
                FROM chunks c
                JOIN documents d ON c.document_id = d.id
            """).fetchall()
            conn.close()

            embeddings = []
            metadata = []
            for r in rows:
                emb = json.loads(r[5]) if r[5] else None
                if emb:
                    embeddings.append(emb)
                    metadata.append({
                        "chunk_id": r[0],
                        "document_id": r[1],
                        "start_ref": r[2] or "00:00:00",
                        "speaker": r[3] or r[6],
                        "text": r[4],
                        "guest": r[6],
                        "title": r[7],
                        "youtube_url": r[8]
                    })

            if embeddings:
                mat = np.array(embeddings, dtype=np.float32)
                norms = np.linalg.norm(mat, axis=1, keepdims=True)
                norms[norms == 0] = 1.0
                mat /= norms
                self.matrix = mat
                self.metadata = metadata
                self._initialized = True

                # Persist cache for fast future boots
                try:
                    os.makedirs(cache_dir, exist_ok=True)
                    np.savez_compressed(npz_file, matrix=mat)
                    with open(meta_file, "w", encoding="utf-8") as f:
                        json.dump(metadata, f)
                    logger.info("vector_search_cache_created", total_chunks=len(metadata))
                except Exception as e:
                    logger.warning("failed_saving_vector_cache", error=str(e))

    async def search(
        self,
        query: str,
        session: Optional[AsyncSession] = None,
        top_k: int = 6,
        rrf_k: int = 60
    ) -> Tuple[List[SearchResult], bool]:
        """
        Executes hybrid search accelerated by NumPy vector operations and candidate pruning.
        Returns (results, is_covered).
        """
        self._ensure_index_loaded()

        if self.matrix is None or not self.metadata:
            logger.warning("no_chunks_found_in_database")
            return [], False

        # 1. Generate query embedding
        query_embedding = await embedding_client.get_embedding(query)
        if not query_embedding:
            return [], False

        q_vec = np.array(query_embedding, dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)
        if q_norm > 0:
            q_vec /= q_norm

        # 2. Fast NumPy matrix-vector dot product (Vector similarity)
        sims = np.dot(self.matrix, q_vec)

        # 3. Build candidate set: top 120 vector candidates + any guest/title keyword matches
        top_indices = set(np.argsort(sims)[::-1][:120])

        raw_tokens = [t for t in re.findall(r"\w+", query.lower()) if t not in STOPWORDS and len(t) > 1]
        if raw_tokens:
            for idx, item in enumerate(self.metadata):
                g = item["guest"].lower()
                t = item["title"].lower()
                if any(token in g or token in t for token in raw_tokens):
                    top_indices.add(idx)

        # 4. Score candidates on lexical overlap and compute RRF
        scored_candidates = []
        for idx in top_indices:
            item = self.metadata[idx]
            v_score = float(sims[idx])
            l_score = lexical_score(query, item["text"], item["guest"], item["title"])
            scored_candidates.append({
                "idx": idx,
                "item": item,
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

        # Reciprocal Rank Fusion (RRF)
        results: List[SearchResult] = []
        for item in scored_candidates:
            v_rank = item["vector_rank"]
            l_rank = item["lexical_rank"]
            rrf = (1.0 / (rrf_k + v_rank)) + (1.0 / (rrf_k + l_rank))
            meta = item["item"]
            results.append(SearchResult(
                chunk_id=meta["chunk_id"],
                document_id=meta["document_id"],
                guest=meta["guest"],
                title=meta["title"],
                youtube_url=meta.get("youtube_url"),
                start_ref=meta.get("start_ref", "00:00:00"),
                speaker=meta.get("speaker", meta["guest"]),
                text=meta["text"],
                vector_score=item["v_score"],
                lexical_score=item["l_score"],
                rrf_score=rrf,
            ))

        # Sort by RRF score descending
        results.sort(key=lambda x: x.rrf_score, reverse=True)
        top_results = results[:top_k]

        # 5. Check threshold cutoff for refusal
        max_v = max((r.vector_score for r in top_results), default=0.0)
        max_l = max((r.lexical_score for r in top_results), default=0.0)

        # High-precision threshold distinguishing genuine podcast queries from out-of-scope topics
        is_covered = (max_v >= 0.58 or max_l >= 5.0)

        logger.info(
            "hybrid_search_completed",
            query=query[:60],
            top_vector_score=round(max_v, 3),
            top_lexical_score=round(max_l, 3),
            is_covered=is_covered
        )

        return top_results, is_covered


hybrid_search = HybridSearchEngine()
