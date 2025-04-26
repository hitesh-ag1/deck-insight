from langgraph.graph import StateGraph
from langchain_core.runnables import RunnableLambda
from langgraph.checkpoint.memory import MemorySaver


from agents.pitch_deck.models import (
    GraphState,
)

from agents.pitch_deck.nodes import (
    OCRSlide,
    SummarizeSlide,
    ScoreSlide,
    should_continue,
    end_state
)
    
graph = StateGraph(GraphState)

# Nodes
graph.add_node("OCRSlide", RunnableLambda(OCRSlide))
graph.add_node("SummarizeSlide", RunnableLambda(SummarizeSlide))
graph.add_node("ScoreSlide", RunnableLambda(ScoreSlide))
graph.add_node("end", RunnableLambda(end_state))

# Flow with conditional routing
graph.set_entry_point("OCRSlide")

# Add conditional edges
graph.add_conditional_edges(
    "OCRSlide",
    should_continue,
    {
        "continue": "SummarizeSlide",
        "end": "end"
    }
)

graph.add_conditional_edges(
    "SummarizeSlide",
    should_continue,
    {
        "continue": "ScoreSlide",
        "end": "end"
    }
)

graph.add_conditional_edges(
    "ScoreSlide",
    should_continue,
    {
        "continue": "end",
        "end": "end"
    }
)

graph.set_finish_point("end")

pitch_deck_agent = graph.compile(checkpointer=MemorySaver())
