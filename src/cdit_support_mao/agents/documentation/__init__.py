"""Documentation agent (Shawn's Lane): verified-fact-only draft notes with manual fallback."""

from cdit_support_mao.agents.documentation.agent import (
    AGENT_NAME,
    AGENT_VERSION,
    DocumentationAgent,
)
from cdit_support_mao.agents.documentation.privacy import scan_for_sensitive_data

__all__ = ["AGENT_NAME", "AGENT_VERSION", "DocumentationAgent", "scan_for_sensitive_data"]
