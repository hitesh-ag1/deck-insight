# agents/supervisor/agent.py

import logging
from typing import Literal, Union
from langchain_core.runnables import RunnableLambda
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver

from agents.pitch_deck.agent import pitch_deck_agent
from agents.market_size.agent import market_research_agent
from agents.github_repo.agent import github_repo_agent
from agents.supervisor.models import (
    GraphState,
    SupervisorResponse,
    PitchDeckAnalysis,
    MarketAnalysis,
    GitHubAnalysis
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_pitch_deck(state: GraphState) -> GraphState:
    """
    Analyzes the pitch deck and extracts key information.
    
    Args:
        state (GraphState): Current state containing slides data
        
    Returns:
        GraphState: Updated state with pitch deck analysis results
    """
    try:
        logger.info("Starting pitch deck analysis")
        
        result = pitch_deck_agent.invoke({
            "slides": state["slides"]
        })
        
        if "error" in result:
            state["error"] = result["error"]
            logger.error(f"Pitch deck analysis failed: {result['error']}")
            return state
        
        # Update state with pitch deck analysis results
        state["summary"] = result["summary"]
        state["scorecard"] = result["scorecard"]
        state["slide_content"] = result.get("slide_content", [])
        
        # Determine if it's a tech company
        tech_keywords = ["saas", "software", "platform", "tech", "technology", 
                        "open source", "api", "cloud", "digital", "ai", 
                        "machine learning", "blockchain"]
        
        summary_text = str(result["summary"]).lower()
        state["is_tech_company"] = any(keyword in summary_text for keyword in tech_keywords)
        
        # Extract GitHub URL if present
        import re
        github_pattern = r'https?://(?:www\.)?github\.com/[\w-]+(?:/[\w-]+)?'
        github_urls = re.findall(github_pattern, str(result["summary"]))
        if github_urls:
            state["github_url"] = github_urls[0]
            
        logger.info("Pitch deck analysis completed successfully")
        return state
        
    except Exception as e:
        error_msg = f"Pitch deck analysis failed: {str(e)}"
        logger.error(error_msg)
        state["error"] = error_msg
        return state

def analyze_market(state: GraphState) -> GraphState:
    """
    Performs market analysis based on pitch deck summary.
    
    Args:
        state (GraphState): Current state containing pitch deck summary
        
    Returns:
        GraphState: Updated state with market analysis results
    """
    try:
        logger.info("Starting market analysis")
        
        if not state["summary"]:
            raise ValueError("No pitch deck summary available for market analysis")
            
        result = market_research_agent.invoke({
            "input_overview": state["summary"]
        })
        
        if "error" in result:
            state["error"] = result["error"]
            logger.error(f"Market analysis failed: {result['error']}")
            return state
            
        # Update state with market analysis results
        state["sector"] = result["sector"]
        state["market_size"] = result["market_size"]
        state["competitors"] = result["competitors"]
        
        logger.info("Market analysis completed successfully")
        return state
        
    except Exception as e:
        error_msg = f"Market analysis failed: {str(e)}"
        logger.error(error_msg)
        state["error"] = error_msg
        return state

def analyze_github(state: GraphState) -> GraphState:
    """
    Analyzes GitHub repository if applicable.
    
    Args:
        state (GraphState): Current state containing GitHub URL
        
    Returns:
        GraphState: Updated state with GitHub analysis results
    """
    try:
        if not state["is_tech_company"] or not state.get("github_url"):
            logger.info("Skipping GitHub analysis (Not a tech company or no GitHub URL)")
            return state
            
        logger.info("Starting GitHub repository analysis")
        
        result = github_repo_agent.invoke({
            "link": state["github_url"]
        })
        
        if "error" in result:
            state["error"] = result["error"]
            logger.error(f"GitHub analysis failed: {result['error']}")
            return state
            
        state["github_details"] = result["repo"]
        
        logger.info("GitHub analysis completed successfully")
        return state
        
    except Exception as e:
        error_msg = f"GitHub analysis failed: {str(e)}"
        logger.error(error_msg)
        state["error"] = error_msg
        return state

def should_continue(state: GraphState) -> Union[Literal["continue"], Literal["end"]]:
    """
    Determines if the analysis should continue based on current state.
    
    Args:
        state (GraphState): Current state of analysis
        
    Returns:
        str: "continue" or "end" based on state
    """
    if state.get("error"):
        return "end"
    return "continue"

def format_response(state: GraphState) -> SupervisorResponse:
    """
    Formats the final response from the state.
    
    Args:
        state (GraphState): Final state containing all analysis results
        
    Returns:
        SupervisorResponse: Formatted response object
    """
    return SupervisorResponse(
        pitch_deck_summary=PitchDeckAnalysis(
            company_overview=state["summary"].get("company_overview"),
            founder_market_fit=state["summary"].get("founder_market_fit"),
            market_sizing=state["summary"].get("market_sizing"),
            traction=state["summary"].get("traction"),
            slide_content=state["slide_content"]
        ),
        pitch_deck_scorecard=state["scorecard"],
        market_analysis=MarketAnalysis(
            sector=state["sector"],
            market_size=state["market_size"],
            competitors=state["competitors"]
        ) if state.get("sector") else None,
        github_analysis=GitHubAnalysis(
            repositories=state["github_details"]
        ) if state.get("github_details") else None,
        is_tech_company=state["is_tech_company"]
    )

def end_state(state: GraphState) -> GraphState:
    """
    Final node that formats and returns the response.
    
    Args:
        state (GraphState): Final state of all analyses
        
    Returns:
        SupervisorResponse: Formatted final response
    """
    if state.get("error"):
        logger.error(f"Analysis ended with error: {state['error']}")
        raise ValueError(state["error"])
        
    logger.info("Analysis completed successfully")
    return state

# Build the supervisor graph
graph = StateGraph(GraphState)

# Add nodes
graph.add_node("pitch_deck_analysis", RunnableLambda(analyze_pitch_deck))
graph.add_node("market_analysis_node", RunnableLambda(analyze_market))
graph.add_node("github_analysis", RunnableLambda(analyze_github))
graph.add_node("end", RunnableLambda(end_state))

# Set entry point
graph.set_entry_point("pitch_deck_analysis")

# Add conditional edges
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

# Set finish point
graph.set_finish_point("end")

# Compile the graph with checkpointing
supervisor_agent = graph.compile(checkpointer=MemorySaver())