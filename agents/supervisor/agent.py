
from langchain_core.runnables import RunnableLambda
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver

from agents.supervisor.models import (
    GraphState,
)

from agents.supervisor.nodes import (
    analyze_pitch_deck,
    analyze_market,
    analyze_github,
    end_state,
    should_continue,
)

graph = StateGraph(GraphState)

graph.add_node("pitch_deck_analysis", RunnableLambda(analyze_pitch_deck))
graph.add_node("market_analysis_node", RunnableLambda(analyze_market))
graph.add_node("github_analysis", RunnableLambda(analyze_github))
graph.add_node("end", RunnableLambda(end_state))

graph.set_entry_point("pitch_deck_analysis")

graph.add_conditional_edges(
    "pitch_deck_analysis",
    should_continue,
    {
        "continue": "market_analysis_node",
        "end": "end"
    }
)

graph.add_conditional_edges(
    "market_analysis_node",
    should_continue,
    {
        "continue": "github_analysis",
        "end": "end"
    }
)

graph.add_conditional_edges(
    "github_analysis",
    should_continue,
    {
        "continue": "end",
        "end": "end"
    }
)

graph.set_finish_point("end")
supervisor_agent = graph.compile(checkpointer=MemorySaver())