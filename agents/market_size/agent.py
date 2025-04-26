from datetime import datetime
from typing import Literal

from langchain_community.tools import DuckDuckGoSearchResults, OpenWeatherMapQueryRun
from langchain_community.utilities import OpenWeatherMapAPIWrapper
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.runnables import RunnableConfig, RunnableLambda, RunnableSerializable
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, MessagesState, StateGraph
from langgraph.managed import RemainingSteps
from langgraph.prebuilt import ToolNode
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import ChatOpenAI
from core.prompts import MARKET_RESEARCH_PROMPT
from core.settings import settings
from agents.market_size.models import (
    GraphState,
    MarketResearchResponse    
)

language_model = ChatOpenAI(model=settings.TEXT_MODEL, temperature=0)
search_tool = TavilySearchResults(k=3)
tools = [search_tool]
language_model = language_model.bind_tools(tools).with_structured_output(MarketResearchResponse)  

def market_research(state: GraphState) -> GraphState:
    try:
        print("--- Step 1: Market Research ---")
        response = language_model.invoke(
            MARKET_RESEARCH_PROMPT + str(state["input_overview"])
        )
        
        state["sector"] = response.sector
        state["market_size"] = response.market_size
        state["competitors"] = response.competitors
        return state
    except Exception as e:
        print(f"Error in market research: {str(e)}")
        state["error"] = f"Market Research failed: {str(e)}"
        return state

def end_state(state: GraphState) -> GraphState:
    """Final node that returns the state as is"""
    return state


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
