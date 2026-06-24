"""Provider-agnostic LLM-agent layer (offline fake provider by default).

The provider lives on the orchestrator side, never inside the MCP servers. No
real external API, API keys, or secrets are involved at this stage.
"""

from mars777_cop_thief.llm.agent import AgentDecision, LlmAgent
from mars777_cop_thief.llm.cost import estimate_cost, estimate_tokens
from mars777_cop_thief.llm.fake_provider import FakeLocalProvider
from mars777_cop_thief.llm.parser import parse_action
from mars777_cop_thief.llm.prompts import build_prompt
from mars777_cop_thief.llm.provider import LlmResponse

__all__ = [
    "AgentDecision",
    "FakeLocalProvider",
    "LlmAgent",
    "LlmResponse",
    "build_prompt",
    "estimate_cost",
    "estimate_tokens",
    "parse_action",
]
