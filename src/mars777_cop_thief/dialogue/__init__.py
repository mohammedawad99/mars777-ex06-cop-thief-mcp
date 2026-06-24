"""Natural-language dialogue layer: message generation and transcript records."""

from mars777_cop_thief.dialogue.messages import compose_message
from mars777_cop_thief.dialogue.transcript import audit_facts, make_message_event

__all__ = ["audit_facts", "compose_message", "make_message_event"]
