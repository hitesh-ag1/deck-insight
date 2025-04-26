from langchain_core.runnables import RunnableLambda
from typing import Dict, Any, Tuple
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain_community.tools.tavily_search import TavilySearchResults
from prompts import SLIDE_TO_TEXT_PROMPT, SUMMARIZE_COMPANY_OVERVIEW_PROMPT, SUMMARIZE_FOUNDER_MARKET_FIT_PROMPT, SUMMARIZE_MARKET_SIZING_PROMPT, SUMMARIZE_TRACTION_PROMPT, SCORING_PROMPT
from google.api_core.exceptions import ResourceExhausted
from agents.pitch_deck.models import (
    CompanyOverview,
    FounderMarketFit,
    MarketSizingGrowth,
    Traction,
    ProcessSlideResponse,
)
from settings import settings

def vision_model_fn(input_dict):
    image_bytes = input_dict["image"]
    prompt = input_dict["prompt"]
    try:
        response = ChatGoogleGenerativeAI(model=settings.VISION_MODEL, google_api_key=settings.GOOGLE_API_KEY).with_structured_output(ProcessSlideResponse).invoke([
            HumanMessage(content=[
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": image_bytes}}
            ])
        ])
        return response
    
    except ResourceExhausted as e:
        print(f"Resource exhausted error: {str(e)}")
        raise  # Let the retry decorator handle it
        
    except Exception as e:
        print(f"Unexpected error occurred: {str(e)}")
        raise  # Let the retry decorator handle it

vision_model = RunnableLambda(vision_model_fn)

language_model = ChatOpenAI(model=settings.TEXT_MODEL, temperature=0)
search_tool = TavilySearchResults(k=3)
summary_tasks = [
        ("Company Overview", language_model, SUMMARIZE_COMPANY_OVERVIEW_PROMPT),
        ("Founder-Market Fit", language_model, SUMMARIZE_FOUNDER_MARKET_FIT_PROMPT),
        ("Market Sizing & Growth", language_model, SUMMARIZE_MARKET_SIZING_PROMPT),
        ("Traction", language_model, SUMMARIZE_TRACTION_PROMPT)
    ]

def process_single_slide(slide_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process a single slide in parallel"""
    image = slide_data["imageByte"]
    
    response = vision_model.invoke({
        "image": image,
        "prompt": SLIDE_TO_TEXT_PROMPT
    })
    
    return {
        "text": response.text,
        "image": response.image,
        "figure": response.figure
    }

def process_summary(summary_type: str, model, prompt: str, slide_content: list) -> Tuple[str, Any]:
    """Process a single summary in parallel"""
    try:
        result = model.with_structured_output(
            {
                "Company Overview": CompanyOverview,
                "Founder-Market Fit": FounderMarketFit,
                "Market Sizing & Growth": MarketSizingGrowth,
                "Traction": Traction
            }[summary_type]
        ).invoke(prompt + str(slide_content))
        return summary_type, result
    except Exception as e:
        print(f"Error processing {summary_type} summary: {str(e)}")
        return summary_type, None
