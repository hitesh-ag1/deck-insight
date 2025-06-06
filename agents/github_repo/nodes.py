from firecrawl import FirecrawlApp
from langchain_openai import ChatOpenAI
from core.settings import settings
from core.prompts import GITHUB_ORG_DETAILS_EXTRACT_PROMPT

from agents.github_repo.models import (
    GraphState,
    Repositories
)

language_model = ChatOpenAI(model=settings.TEXT_MODEL, temperature=0).with_structured_output(Repositories)

def github_repo(state: GraphState) -> GraphState:
    try:
        print("--- Step 1: Get Github Repos ---")
        app = FirecrawlApp(api_key=settings.FIRECRAWL_API_KEY)
        scrape_result = app.scrape_url(state['link'], formats=['markdown'])
        response = language_model.invoke(
            GITHUB_ORG_DETAILS_EXTRACT_PROMPT + str(scrape_result.markdown)
        )
        state["repo"] = response
        return state
    except Exception as e:
        print(f"Error in getting details : {str(e)}")
        state["error"] = f"Github scraping failed: {str(e)}"
        return state

def end_state(state: GraphState) -> GraphState:
    """Final node that returns the state as is"""
    return state

