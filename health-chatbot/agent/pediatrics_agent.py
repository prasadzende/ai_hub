from typing import Dict
from langchain_core.messages import HumanMessage
from utils.graph_utils import prepend_system_once
from prompt_library.prompt import PEDIATRICS_SYSTEM

def pediatrics_step(messages, llm_with_tools) -> Dict:
    last = messages[-1] if messages else None
    if getattr(last, "type", None) == "tool":
        messages = messages + [HumanMessage(content="Use the tool results above and provide a final pediatrics answer without calling tools.")]
    augmented = prepend_system_once(messages, PEDIATRICS_SYSTEM)
    ai = llm_with_tools.invoke(augmented)
    return {"messages": [ai]}
