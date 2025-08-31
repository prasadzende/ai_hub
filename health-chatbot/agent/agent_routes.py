from langchain_core.messages import AIMessage, HumanMessage
from utils.graph_utils import CARDIO_KW, PED_KW, SMALL_TALK
from utils.graph_utils import has_valid_tool_calls
from langgraph.graph import END

def receptionist_route(state):
    msgs = state["messages"]
    if not msgs:
        return END
    last_ai = next((m for m in reversed(msgs) if isinstance(m, AIMessage)), None)
    last_user = next((m for m in reversed(msgs) if isinstance(m, HumanMessage)), None)
    user_text = (last_user.content or "").lower() if last_user else ""

    if any(p in user_text for p in SMALL_TALK):
        return END
    if last_ai and has_valid_tool_calls(last_ai):
        return "tools"
    if any(k in user_text for k in CARDIO_KW):
        return "cardiology"
    if any(k in user_text for k in PED_KW):
        return "pediatrics"
    if any(k in user_text for k in ("report", "lab", "patient", "record", "database", "result", "scan")):
        return "tools"
    return END

def post_tools_router(state) -> str:
    msgs = state["messages"]
    last_user = next((m for m in reversed(msgs) if isinstance(m, HumanMessage)), None)
    user_text = (last_user.content or "").lower() if last_user else ""
    if any(k in user_text for k in CARDIO_KW):
        return "cardiology"
    if any(k in user_text for k in PED_KW):
        return "pediatrics"
    return "reception"
