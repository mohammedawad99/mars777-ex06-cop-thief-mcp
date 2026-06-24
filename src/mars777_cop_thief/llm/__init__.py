"""Provider-agnostic LLM-agent layer (offline fake provider by default).

The provider lives on the orchestrator side, never inside the MCP servers. No
real external API, API keys, or secrets are involved at this stage.
"""

from mars777_cop_thief.llm.agent import AgentDecision, LlmAgent
from mars777_cop_thief.llm.config import LlmConfigError, load_llm_config
from mars777_cop_thief.llm.cost import estimate_cost, estimate_tokens
from mars777_cop_thief.llm.fake_provider import FakeLocalProvider
from mars777_cop_thief.llm.gemini_provider import GeminiProvider
from mars777_cop_thief.llm.parser import parse_action
from mars777_cop_thief.llm.prompts import build_prompt
from mars777_cop_thief.llm.provider import LlmResponse
from mars777_cop_thief.llm.provider_factory import create_provider_from_env

__all__ = [
    "AgentDecision",
    "FakeLocalProvider",
    "GeminiProvider",
    "LlmAgent",
    "LlmConfigError",
    "LlmResponse",
    "build_prompt",
    "create_provider_from_env",
    "estimate_cost",
    "estimate_tokens",
    "load_llm_config",
    "parse_action",
]
