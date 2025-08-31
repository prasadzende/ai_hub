from pathlib import Path
import sys

# ROOT = Path(__file__).resolve().parents[10]
# if str(ROOT) not in sys.path:
#     sys.path.insert(0, str(ROOT))

from typing import List
from langchain.tools import BaseTool
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import InMemorySaver

from utils.model_loader import ModelLoader
from tools.vanna_tool import VannaTool

# Import modular agents and routing
from agent.reception_agent import receptionist_step
from agent.cardiologist_agent import cardiology_step
from agent.pediatrics_agent import pediatrics_step
from utils.graph_utils import has_valid_tool_calls
from agent.agent_routes import post_tools_router, receptionist_route

class MultiAgentApp:
    def __init__(self, model_provider: str = "lmstudio") -> None:
        self.model_loader = ModelLoader(model_provider=model_provider)
        self.llm = self.model_loader.load_llm()

        self.vanna_tools = VannaTool(client=self.llm, config={"model": "local-model"})
        self.tools: List[BaseTool] = [*self.vanna_tools.vanna_tool_list]
        self.llm_with_tools = self.llm.bind_tools(tools=self.tools)

        self.memory = InMemorySaver()

    def tools_condition(self, state: MessagesState) -> str:
        msgs = state["messages"]
        if not msgs:
            return END
        last_ai = next((m for m in reversed(msgs) if m.__class__.__name__ == "AIMessage"), None)
        if last_ai and has_valid_tool_calls(last_ai):
            return "tools"
        return END

    def build(self):
        g = StateGraph(MessagesState)

        # Wrap agent steps so they receive the proper model binding
        g.add_node("reception", lambda s: receptionist_step(s["messages"], self.llm))
        g.add_node("cardiology", lambda s: cardiology_step(s["messages"], self.llm_with_tools))
        g.add_node("pediatrics", lambda s: pediatrics_step(s["messages"], self.llm_with_tools))

        g.add_node("tools", ToolNode(self.tools))

        g.add_edge(START, "reception")

        g.add_conditional_edges(
            "reception",
            receptionist_route,
            {"tools": "tools", "cardiology": "cardiology", "pediatrics": "pediatrics", END: END},
        )

        g.add_conditional_edges(
            "tools",
            post_tools_router,
            {"cardiology": "cardiology", "pediatrics": "pediatrics", "reception": "reception"},
        )

        g.add_conditional_edges(
            "cardiology",
            self.tools_condition,
            {"tools": "tools", END: END},
        )
        g.add_conditional_edges(
            "pediatrics",
            self.tools_condition,
            {"tools": "tools", END: END},
        )
        g = g.compile(checkpointer=self.memory)
        png_graph = g.get_graph().draw_mermaid_png()
        with open("my_graph.png", "wb") as f:
            f.write(png_graph)
        return g

    def __call__(self):
        return self.build()
