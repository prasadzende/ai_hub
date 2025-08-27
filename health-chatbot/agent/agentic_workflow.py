from pathlib import Path
import sys

# Resolve the project root as the parent of the current file's directory.
# Adjust .parent count to reach your repository root.
ROOT = Path(__file__).resolve().parent.parent  # health-chatbot/
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from typing import Dict, List, Any
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from langchain.tools import BaseTool
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode  # Changed from ToolExecutor
from utils.model_loader import ModelLoader
from prompt_library.prompt import SYSTEM_PROMPT
from tools.vanna_tool import VannaTool


class GraphBuilder:
    def __init__(self, model_provider: str = "lmstudio") -> None:
        """Initialize the graph builder with model and tools."""
        self.model_loader = ModelLoader(model_provider=model_provider)
        self.llm = self.model_loader.load_llm()
        
        # Initialize tools
        self.vanna_tools = VannaTool(client=self.llm, config={'model': 'local-model'})
        self.tools: List[BaseTool] = [*self.vanna_tools.vanna_tool_list]
        
        # Bind tools to LLM
        self.llm_with_tools = self.llm.bind_tools(tools=self.tools)
        self.system_prompt = SYSTEM_PROMPT
        self.graph = None

    def agent_function(self, state: MessagesState) -> Dict:
        """Process messages and generate response."""
        try:
            messages = state["messages"]  # MessagesState uses "messages" key
            
            # Add system prompt if not already present
            if not messages or not any(isinstance(m, HumanMessage) and 
                                     str(self.system_prompt) in m.content 
                                     for m in messages):
                augmented_messages = [
                    HumanMessage(content=str(self.system_prompt))
                ] + messages
            else:
                augmented_messages = messages
            print("=======aug message", augmented_messages)
            response = self.llm_with_tools.invoke(augmented_messages)
            return {"messages": [response]}  # Return new messages to add
            
        except Exception as e:
            print(f"Agent error: {str(e)}")
            error_response = AIMessage(content="I encountered an error. Please try again.")
            return {"messages": [error_response]}

    def should_use_tool(self, state: MessagesState) -> str:
        """Route to tools or end based on agent response."""
        messages = state["messages"]
        if not messages:
            return END
            
        last_message = messages[-1]
        tool_calls = getattr(last_message, "tool_calls", None)
        if isinstance(tool_calls, list) and any(tc for tc in tool_calls if tc):
            return "tools"
        return END

    def build_graph(self):
        """Build and compile the workflow graph."""
        try:
            # Create the StateGraph
            workflow = StateGraph(MessagesState)
            
            # Add nodes
            workflow.add_node("agent", self.agent_function)
            
            # Use ToolNode instead of ToolExecutor
            tool_node = ToolNode(self.tools)
            workflow.add_node("tools", tool_node)
            
            # Add edges
            workflow.add_edge(START, "agent")
            workflow.add_conditional_edges(
                "agent",
                self.should_use_tool,
                {
                    "tools": "tools",
                    END: END
                }
            )
            workflow.add_edge("tools", "agent")
            
            # Compile the graph
            
            return workflow.compile()
            
        except Exception as e:
            print(f"Graph build error: {str(e)}")
            raise

    def __call__(self):
        """Make the class callable."""
        return self.build_graph()
