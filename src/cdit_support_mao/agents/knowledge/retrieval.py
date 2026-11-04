"""Local lexical retrieval (BM25) over approved knowledge sections.

No external vector service or model is used (PRD "Recommended prototype stack").
The ``coverage`` score is an explainable, provisional evidence-strength signal:
the IDF-weighted share of query terms that appear in a section. It is not a
calibrated probability (deferred decision D-08).
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass

from cdit_support_mao.agents.knowledge.corpus import KbArticle, KbSection, KnowledgeCorpus

BM25_K1 = 1.5
BM25_B = 0.75

_TOKEN = re.compile(r"[a-z0-9]+")

STOPWORDS = frozenset(
    """
    a about after again all also am an and any are as asks at be been before being but by
    can cannot could did do does doing for from get gets got had has have having he her hers
    him his how i if in into is it its just me my need needs no not now of on once only or
    our out over please she should so some still such than that the their them then there
    these they this those through to too under until up us very was we were what when where
    which while who whom why will with would you your yours
    hi hello thanks thank help issue problem ticket user users customer customers unable trying
    able try tried says said asked wants want
    """.split()
)


def _stem(token: str) -> str:
    if len(token) > 4 and token.endswith("ies"):
        return token[:-3] + "y"
    if len(token) > 5 and token.endswith("ing"):
        return token[:-3]
    if len(token) > 4 and token.endswith("ed") and not token.endswith("eed"):
        return token[:-2]
    if len(token) > 3 and token.endswith("s") and not token.endswith("ss"):
        return token[:-1]
    return token


def tokenize(text: str) -> list[str]:
    """Lowercase, split on non-alphanumerics, drop stopwords and 1-char tokens, light stemming."""
    return [_stem(t) for t in _TOKEN.findall(text.lower()) if len(t) > 1 and t not in STOPWORDS]


def section_index_text(article: KbArticle, section: KbSection) -> str:
    """Text that is searchable. Stop conditions are excluded to avoid matching risk wording."""
    parts = [article.title, section.heading, section.text, " ".join(article.keywords)]
    parts.extend(step.text for step in section.steps)
    return " ".join(parts)


@dataclass(frozen=True)
class IndexedSection:
    article: KbArticle
    section: KbSection
    term_counts: Counter[str]
    length: int


@dataclass(frozen=True)
class ScoredSection:
    indexed: IndexedSection
    bm25: float
    coverage: float
    matched_terms: tuple[str, ...]

    @property
    def article(self) -> KbArticle:
        return self.indexed.article

    @property
    def section(self) -> KbSection:
        return self.indexed.section


class LexicalIndex:
    """BM25 index over every section of every article (eligibility is decided later)."""

    def __init__(self, corpus: KnowledgeCorpus) -> None:
        self._sections: list[IndexedSection] = []
        for article in corpus.articles:
            for section in article.sections:
                terms = tokenize(section_index_text(article, section))
                self._sections.append(IndexedSection(article, section, Counter(terms), len(terms)))
        count = len(self._sections)
        self._avg_length = sum(s.length for s in self._sections) / count if count else 0.0
        document_frequency: Counter[str] = Counter()
        for indexed in self._sections:
            document_frequency.update(indexed.term_counts.keys())
        self._idf = {
            term: math.log(1 + (count - df + 0.5) / (df + 0.5))
            for term, df in document_frequency.items()
        }
        # Unseen query terms count with the average IDF so off-topic words lower coverage.
        self._unseen_idf = sum(self._idf.values()) / len(self._idf) if self._idf else 1.0

    def idf(self, term: str) -> float:
        return self._idf.get(term, self._unseen_idf)

    def search(self, query: str) -> list[ScoredSection]:
        """Return sections with at least one matching term, best coverage first."""
        query_terms = sorted(set(tokenize(query)))
        if not query_terms:
            return []
        total_weight = sum(self.idf(term) for term in query_terms)
        results: list[ScoredSection] = []
        for indexed in self._sections:
            matched = tuple(t for t in query_terms if indexed.term_counts.get(t))
            if not matched:
                continue
            bm25 = 0.0
            for term in matched:
                tf = indexed.term_counts[term]
                norm = BM25_K1 * (1 - BM25_B + BM25_B * indexed.length / self._avg_length)
                bm25 += self.idf(term) * tf * (BM25_K1 + 1) / (tf + norm)
            coverage = sum(self.idf(t) for t in matched) / total_weight
            results.append(ScoredSection(indexed, bm25, round(min(coverage, 1.0), 4), matched))
        results.sort(
            key=lambda s: (-s.coverage, -s.bm25, s.article.doc_id, s.article.version, s.section.section_id)
        )
        return results

    @staticmethod
    def query_term_count(query: str) -> int:
        return len(set(tokenize(query)))
