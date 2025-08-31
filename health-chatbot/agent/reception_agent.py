from typing import Dict
from langgraph.graph import MessagesState, END
from prompt_library.prompt import RECEPTIONIST_SYSTEM
from langchain_core.messages import (
    BaseMessage,
    AIMessage,
    HumanMessage,
    SystemMessage,
)
from utils.graph_utils import has_valid_tool_calls, prepend_system_once, PED_KW, CARDIO_KW, SMALL_TALK

# ---------- Receptionist router ----------
def receptionist_step(messages, llm_no_tools) -> Dict:
    # Small talk: answer directly without tools
    last_user = next((m for m in reversed(messages) if isinstance(m, HumanMessage)), None)
    if last_user:
        txt = (last_user.content or "").lower()
        if any(p in txt for p in SMALL_TALK):
            augmented = prepend_system_once(messages, RECEPTIONIST_SYSTEM)
            ai = llm_no_tools.invoke(augmented)
            return {"messages": [ai]}
    # Default: receptionist answers without tools
    augmented = prepend_system_once(messages, RECEPTIONIST_SYSTEM)
    ai = llm_no_tools.invoke(augmented)
    return {"messages": [ai]}

def receptionist_route(state) -> str:
    msgs = state["messages"]
    if not msgs:
        return "END"
    last_ai = next((m for m in reversed(msgs) if isinstance(m, AIMessage)), None)
    last_user = next((m for m in reversed(msgs) if isinstance(m, HumanMessage)), None)
    user_text = (last_user.content or "").lower() if last_user else ""

    if any(p in user_text for p in SMALL_TALK):
        return "END"
    if last_ai and has_valid_tool_calls(last_ai):
        return "tools"
    if any(k in user_text for k in CARDIO_KW):
        return "cardiology"
    if any(k in user_text for k in PED_KW):
        return "pediatrics"
    if any(k in user_text for k in ("report", "lab", "patient", "record", "database", "result", "scan")):
        return "tools"
    return "END"