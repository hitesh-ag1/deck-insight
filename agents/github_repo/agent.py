from langgraph.graph import StateGraph
from langchain_core.runnables import RunnableLambda
from langgraph.checkpoint.memory import MemorySaver
from agents.github_repo.models import (
    GraphState,
)

from agents.github_repo.nodes import (
    github_repo,
    end_state
)

graph = StateGraph(GraphState)
graph.add_node("github_repo", RunnableLambda(github_repo))
graph.add_node("end", RunnableLambda(end_state))

graph.set_entry_point("github_repo")
graph.set_finish_point("end")
graph.add_edge("github_repo", "end")

github_repo_agent = graph.compile(checkpointer=MemorySaver())
