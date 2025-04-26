from langchain_core.runnables import RunnableLambda
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode
from agents.market_size.models import (
    GraphState,
)
from agents.market_size.nodes import (
    market_research,
    end_state,
    tools
)

graph = StateGraph(GraphState)
graph.add_node("market_research", RunnableLambda(market_research))
graph.add_node("tools", ToolNode(tools))
graph.add_node("end", RunnableLambda(end_state))

graph.set_entry_point("market_research")

graph.add_edge("tools", "market_research")
graph.add_conditional_edges(
    "market_research",
    lambda x: "tools" if x.get("error") is None and x.get("needs_tools", False) else "end",
    {
        "tools": "tools",
        "end": "end"
    }
)
graph.set_finish_point("end")

market_research_agent = graph.compile()
