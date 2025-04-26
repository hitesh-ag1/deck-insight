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
