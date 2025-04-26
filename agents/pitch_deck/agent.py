from langgraph.graph import StateGraph
from langchain_core.runnables import RunnableLambda
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Union, Literal
from langchain_elasticsearch import ElasticsearchStore
from langchain_openai import OpenAIEmbeddings
from settings import settings
from uuid import uuid4
from langchain_core.documents import Document
from langgraph.checkpoint.memory import MemorySaver

from agents.pitch_deck.helpers import (
    language_model,
    summary_tasks,
    SCORING_PROMPT,
    process_single_slide,
    process_summary,
)

from agents.pitch_deck.models import (
    GraphState,
    ScoringResponseList
)

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

# --- Step 1: OCR Slide Agent ---
def OCRSlide(state: GraphState) -> Union[GraphState, dict]:
    try:
        slide_content = []
        workers = os.cpu_count() + 4
        max_workers = min(len(state["slides"]), workers)
        
        print("--- Step 1: OCR Task ---")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_slide = {
                executor.submit(process_single_slide, state["slides"][i]): i 
                for i in range(len(state["slides"]))
            }
            
            for future in as_completed(future_to_slide):
                slide_index = future_to_slide[future]
                try:
                    result = future.result()
                    state["slides"][slide_index]["text"] = result["text"]
                    state["slides"][slide_index]["image"] = result["image"] 
                    state["slides"][slide_index]["figure"] = result["figure"]
                    slide_content.append(
                        {
                            "index": slide_index, 
                            "text": result["text"], 
                            "image": result["image"], 
                            "figure": result["figure"]
                        }
                    )
                    print(f"\t Processing slide {slide_index + 1}/{len(state['slides'])}")
                except Exception as e:
                    return {"error": f"Failed to process slide {slide_index + 1}: {str(e)}"}
        
        state["slide_content"] = slide_content
        return state
    except Exception as e:
        return {"error": f"OCR Task failed: {str(e)}"}

# --- Step 2: Summarize Slide Agent ---
def SummarizeSlide(state: GraphState) -> Union[GraphState, dict]:
    try:
        print("--- Step 2: Summarizer Task ---")
        
        summary = {}
        workers = os.cpu_count()
        with ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_summary = {
                executor.submit(process_summary, task[0], task[1], task[2], state["slide_content"]): task[0]
                for task in summary_tasks
            }
            
            for future in as_completed(future_to_summary):
                summary_type = future_to_summary[future]
                try:
                    result_type, result = future.result()
                    summary[result_type] = result
                    print(f"\t Processing {result_type} summary")
                except Exception as e:
                    return {"error": f"Failed to process summary for {summary_type}: {str(e)}"}
        
        elastic_vector_search = ElasticsearchStore(
            es_url=settings.ELASTIC_SEARCH_URL,
            index_name="pitch-deck-ai",
            embedding=embeddings,
            es_api_key=settings.ELASTIC_SEARCH_API,
        )

        document_1 = Document(
            page_content=str(summary),
            metadata={"id": "0002"},
        )

        elastic_vector_search.add_documents(documents=[document_1])

        state["summary"] = summary
        return state
    except Exception as e:
        return {"error": f"Summarizer Task failed: {str(e)}"}

# --- Step 3: Scorecard Generator ---
def ScoreSlide(state: GraphState) -> Union[GraphState, dict]:
    try:
        print("--- Step 3: Scoring Task ---")
        scorecard = language_model.with_structured_output(ScoringResponseList).invoke(
            SCORING_PROMPT + str(state["summary"])
        )
        res = []
        for i in range(len(scorecard.scores)):
            res.append(dict(scorecard.scores[i]))

        state["scorecard"] = res
        return state
    except Exception as e:
        return {"error": f"Scoring Task failed: {str(e)}"}

def should_continue(state: Union[GraphState, dict]) -> Union[Literal["continue"], Literal["end"]]:
    """Determine if the graph should continue or end based on the state"""
    if isinstance(state, dict) and "error" in state:
        return "end"
    return "continue"

def end_state(state: Union[GraphState, dict]) -> Union[GraphState, dict]:
    """Final node that returns the state as is"""
    return state

# --- Step 4: Build Graph ---
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
