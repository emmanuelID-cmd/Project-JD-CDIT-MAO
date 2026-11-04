"""Knowledge agent (Shawn's Lane): approved, versioned retrieval with abstention."""

from cdit_support_mao.agents.knowledge.agent import AGENT_NAME, AGENT_VERSION, KnowledgeAgent
from cdit_support_mao.agents.knowledge.corpus import (
    CorpusError,
    KnowledgeCorpus,
    default_knowledge_dir,
    load_corpus,
)

__all__ = [
    "AGENT_NAME",
    "AGENT_VERSION",
    "CorpusError",
    "KnowledgeAgent",
    "KnowledgeCorpus",
    "default_knowledge_dir",
    "load_corpus",
]
