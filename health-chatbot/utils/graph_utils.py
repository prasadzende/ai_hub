from typing import Any, List
from langchain_core.messages import (
    BaseMessage,
    AIMessage,
    HumanMessage,
    SystemMessage,
)
from prompt_library.prompt import GLOBAL_POLICY, TOOL_USE_POLICY

# Small-talk/identity patterns to avoid unnecessary tool calls or specialist routing
SMALL_TALK = ("who are you", "what are you", "your name", "hello", "hi", "help")

CARDIO_KW = ("heart", "cardio", "ecg", "cholesterol", "lipid", "bp", "blood pressure", "angina", "palpitation", "chest pain")
PED_KW = ("child", "kid", "pediatric", "fever in child", "vaccin", "immuniz", "growth chart", "rash in child", "baby")

def prepend_system_once(messages: List[BaseMessage], system_text: str) -> List[BaseMessage]:
    has_system = any(isinstance(m, SystemMessage) and (system_text in (m.content or "")) for m in messages)
    if has_system:
        return messages
    return [SystemMessage(content=system_text + "\n" + TOOL_USE_POLICY + "\n" + GLOBAL_POLICY), *messages]

def has_valid_tool_calls(msg: Any) -> bool:
    tool_calls = getattr(msg, "tool_calls", None)
    if not isinstance(tool_calls, list):
        return False
    # treat non-empty list of dicts with a "name" as valid
    return any(isinstance(tc, dict) and tc.get("name") for tc in tool_calls)